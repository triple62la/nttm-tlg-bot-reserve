import telebot.types
import socket


def initialize_handlers(bot, subscribers_storage):
    @bot.message_handler(commands=["start"])
    async def show_commands(message: telebot.types.Message):
        await bot.send_message(message.chat.id,
                               """/sub - подписаться на тикеты
                               /unsub - отписаться от тикетов
                               /ip - показать ip текущей машины""")

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
        if message.chat.id not in subs:
            await subscribers_storage.add_subscriber(message.chat.id)
            await bot.send_message(message.chat.id, f"""Вы будете получать в этот чат новые тикеты""")
        else:
            await bot.send_message(message.chat.id, f"""Этот чат уже был подписан на получение новых тикетов""")

    @bot.message_handler(commands=["unsub"])
    async def remove_subscriber(message: telebot.types.Message):
        await subscribers_storage.remove_subscriber(message.chat.id)
        await bot.send_message(message.chat.id, f"""Этот чат отписан от получения новых тикетов""")