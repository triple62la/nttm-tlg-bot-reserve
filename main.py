import sys


import telebot.asyncio_helper
from telebot.async_telebot import AsyncTeleBot
import asyncio
from nttm.nttm_api import TTMApi
from storage.models.subscribers_storage import Subscribers
from storage.models.tickets_storage import TicketsStorage
from storage.models.reports_storage import ReportsStorage
import bot_handlers
from utils import find_tt, load_config, ExceptionHandler
from console import title, Loader

# check_single_instance()


loader = Loader()
subscribers_storage = Subscribers()
tickets_storage = TicketsStorage()
reports_storage = ReportsStorage()
tlg_exc_handler = ExceptionHandler(err_loger=print)
config = load_config()

ttm_api = TTMApi(config)
bot = AsyncTeleBot(token=config["bot_token"], exception_handler=tlg_exc_handler)
bot_handlers.initialize_handlers(bot, ttm_api, subscribers_storage)


def _passes_conditions(tt):
    return not tt["executor"] and \
           tt["execUnit"] == "ЛЦК Wi-Fi ДЭФИР"


async def parse(data):
    tt_to_send = []
    tt_to_remove = []
    storage = await tickets_storage.get_list()
    for tt in data:
        already_sent = await tickets_storage.includes(tt["ticketId"])
        if _passes_conditions(tt) and not already_sent:
            tt_to_send.append(tt)
        elif already_sent and not _passes_conditions(tt):
            tt_to_remove.append(tt)
    for tt in storage:
        in_data = find_tt(data, tt["ticketId"])
        if not in_data:
            tt_to_remove.append(tt)

    return tt_to_send, tt_to_remove


async def send_result(sub_chat_id, ticket):
    return await bot.send_message(sub_chat_id, "Новый ТТ: " + str(ticket["ticketId"]))


async def send_results(parsed_tickets):
    for ticket in parsed_tickets:
        if not await tickets_storage.includes(ticket["ticketId"]):
            msgs_arr = ticket.get("messages", [])
            for sub in await subscribers_storage.get_subscribers():
                msg = await send_result(sub["chat_id"], ticket)
                msgs_arr.append({"chat_id": msg.chat.id, "id": msg.id})
            ticket["messages"] = msgs_arr
            await tickets_storage.add(ticket)


async def remove_results(tts_to_remove):
    for tt in tts_to_remove:
        messages = await tickets_storage.get_messages(tt["ticketId"])
        for msg in messages:
            try:
                result = await bot.delete_message(msg["chat_id"], msg["id"])
            except telebot.asyncio_helper.ApiException:
                continue
            await asyncio.sleep(1)
        await tickets_storage.remove(tt["ticketId"])


async def report_problem(problem_msg):
    subscribers = await subscribers_storage.get_subscribers()
    for sub in subscribers:
        msg = await bot.send_message(sub["chat_id"], problem_msg)
        await reports_storage.add({"chat_id": msg.chat.id, "id": msg.id})


async def remove_reports():
    async def del_msg(report):
        await bot.delete_message(report["chat_id"], report["id"])

    reports = await reports_storage.get_list()
    if not reports:
        return
    task_list = [asyncio.create_task(del_msg(rep)) for rep in reports]
    await asyncio.gather(*task_list)
    await reports_storage.reset()


async def set_interval(callback, sec):
    while True:
        await callback()
        await loader.countdown("Ожидание", start_from=sec)


async def nttm_polling():
    if not ttm_api.isAuthorized:
        await ttm_api.authorize_with_annonce()
    data = await ttm_api.fetch_tickets_with_announce()
    tts_to_send, tts_to_remove = await parse(data)
    await send_results(tts_to_send)
    await remove_results(tts_to_remove)


async def main():
    print(title)
    err = None
    try:
        await remove_reports()
        bot_coro = asyncio.create_task(bot.polling())
        nttm_coro = asyncio.create_task(set_interval(nttm_polling, config["polling_interval"]))
        await asyncio.gather(bot_coro, nttm_coro)
    except KeyboardInterrupt:
        err = "Прервано пользователем"
        sys.exit(-1)
    except Exception as e:
        print(f"\rВ работе главного процесса произошла ошибка: {e}")
        await report_problem(f"В работе главного процесса произошла ошибка: {e} .")
        err = f"В работе главного процесса произошла ошибка: {e} Необходим перезапуск программы."
    finally:
        if err and err != "Прервано пользователем":
            input("Нажмите любую клавишу")


if __name__ == "__main__":
    asyncio.run(main())
