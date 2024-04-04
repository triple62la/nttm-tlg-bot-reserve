import asyncio

import telebot.types
import socket
from telebot.async_telebot import AsyncTeleBot
from nttm.nttm_api import TTMApi
from storage.models.tickets_storage import TicketsStorage

tickets_storage = TicketsStorage()


def results_mapper(result):
    if result:
        return "👍🏻"
    else:
        return "❌"


def initialize_handlers(bot: AsyncTeleBot, ttm_api: TTMApi, subscribers_storage):
    @bot.message_handler(commands=["start"])
    async def show_commands(message: telebot.types.Message):
        await bot.send_message(message.chat.id,
                               """/sub - подписаться на тикеты
                               /unsub - отписаться от тикетов
                               /sub_reports
                               /diag - выполнить диагностику бота(сообщение с результатами удаляется через 15с)
                               /ip - показать ip машины на которой запущен бот
                               /help - памятка -  как пользоваться ботом""")

    @bot.message_handler(commands=["terminate"])
    async def quit_program(message: telebot.types.Message):
        await bot.send_message(message.chat.id, """Выходим из программы""")
        quit(0)

    @bot.message_handler(commands=["ip"])
    async def show_commands(message: telebot.types.Message):
        hostname = socket.gethostname()
        await bot.send_message(message.chat.id, f"""{hostname} IP: {socket.gethostbyname(hostname)}""")

    @bot.message_handler(commands=["sub"])
    async def add_subscriber(message: telebot.types.Message):
        subs = await subscribers_storage.get_list()
        for sub in subs:
            if message.chat.id  == sub["chat_id"]:
                await bot.send_message(message.chat.id, f"""Этот чат уже был подписан на получение новых тикетов""")
                return
        await subscribers_storage.add_subscriber(message.chat.id)
        await bot.send_message(message.chat.id,
                               f"""Вы будете получать в этот чат новые тикеты, а так же сообщения об ошибках""")



    @bot.message_handler(commands=["unsub"])
    async def remove_subscriber(message: telebot.types.Message):
        subscriber = message.chat.id
        await subscribers_storage.remove_subscriber(subscriber)
        sent_tt = await tickets_storage.get_list()
        for tt in sent_tt:
            messages = tt.get("messages", [])
            for msg in messages:
                if msg["chat_id"] == subscriber:
                    await bot.delete_message(msg["chat_id"], msg["id"])
        await bot.send_message(message.chat.id, f"""Этот чат отписан от получения новых тикетов""")

    @bot.message_handler(commands=["diag"])
    async def do_diagnostics(message: telebot.types.Message):
        chat = message.chat.id
        await asyncio.sleep(1)
        await bot.delete_message(chat, message.id)
        info_msg = await bot.send_message(chat, "Ожидание окончания диагностики")
        results = await ttm_api.do_diag()
        await bot.delete_message(chat, info_msg.id)
        msg = f"""Авторизация в NTTM  - {results_mapper(results['auth'])}
        Получение тикетов в NTTM  - {results_mapper(results['fetch'])}"""
        diag_msg = await bot.send_message(chat, msg)
        await asyncio.sleep(10)
        await bot.delete_message(chat, diag_msg.id)

    # @bot.message_handler(commands=["sub_reports"])
    # async def sub_to_reports(message: telebot.types.Message):
    #     chat = message.chat.id
    #     await subscribers_storage.set_allow_reports(chat, True)
    #
    # @bot.message_handler(commands=["unsub_reports"])
    # async def unsub_from_reports(message: telebot.types.Message):
    #     chat = message.chat.id
    #     await subscribers_storage.set_allow_reports(chat, False)

    # @bot.message_handler(commands=["sub&reports"])
    # async def add_sub_with_reports(message: telebot.types.Message):
    #     chat_id = message.chat.id
    #     subs = await subscribers_storage.get_list()
    #     for sub in subs:
    #         if sub["chat_id"] == chat_id and sub["allow_reports"]:
    #             await bot.send_message(message.chat.id,
    #                                    f"""Этот чат уже был подписан на получение новых тикетов и сообщений об ошибках""")
    #
    #         elif sub["chat_id"] == chat_id and not sub["allow_reports"]:
    #             await subscribers_storage.set_allow_reports(chat_id, True)
    #             await bot.send_message(message.chat.id,
    #                                    f"""Вы будете получать в этот чат новые тикеты, а так же сообщения об ошибках""")
    #         else:
    #             await subscribers_storage.add_subscriber(message.chat.id, allow_reports=True)
    #             await bot.send_message(message.chat.id,
    #                                    f"""Вы будете получать в этот чат новые тикеты, а так же сообщения об ошибках""")
