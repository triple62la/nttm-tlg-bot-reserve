from telebot.async_telebot import AsyncTeleBot
import asyncio
from ttm import TTMApi
from storage.models.subscribers_storage import Subscribers
from storage.models.tickets_storage import TicketsStorage
import bot_handlers
from utils import Loader, find_tt, get_config

subscribers_storage = Subscribers()
tickets_storage = TicketsStorage()
config = get_config()
bot = AsyncTeleBot(token=config["token"])
bot_handlers.initialize_handlers(bot, subscribers_storage)
login, passw, url = (config["login"], config["password"], config["nttm_url"])
ttm_api = TTMApi(login, passw, url, print)
loader = Loader()


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
            for sub_chat_id in await subscribers_storage.get_subscribers():
                msg = await send_result(sub_chat_id, ticket)
                msgs_arr.append({"chat_id": msg.chat.id, "id": msg.id})
            ticket["messages"] = msgs_arr
            await tickets_storage.add(ticket)


async def remove_results(tts_to_remove):
    for tt in tts_to_remove:
        messages = await tickets_storage.get_messages(tt["ticketId"])
        for msg in messages:
            result = await bot.delete_message(msg["chat_id"], msg["id"])
            await asyncio.sleep(1)
        await tickets_storage.remove(tt["ticketId"])


async def send_notification(msg):
    subscribers = await subscribers_storage.get_subscribers()
    for sub in subscribers:
        await bot.send_message(sub, msg)


async def set_interval(callback, sec):
    while True:
        await asyncio.sleep(sec)
        await callback()


async def nttm_polling():
    # await loader.start()
    data = await ttm_api.fetch_tickets()
    tts_to_send, tts_to_remove = await parse(data)
    await send_results(tts_to_send)
    await remove_results(tts_to_remove)


async def main():
    try:
        await ttm_api.authorize()
        bot_coro = asyncio.create_task(bot.polling())
        nttm_coro = asyncio.create_task(set_interval(nttm_polling, 5))
        loader_coro = asyncio.create_task(loader.start())
        await asyncio.gather(bot_coro, nttm_coro, loader_coro)
    except Exception as e:
        print(f"В работе главного процесса произошла ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
