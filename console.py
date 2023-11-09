import asyncio
import sys

title = """
╔════╗░╔╗░░░░░░░░░░░░░░░░░░░░░░╔══╗╔═══╦════╗░░░░ 
║╔╗╔╗║░║║░░░░░░░░░░░░░░░░░░░░░░║╔╗║║░═╗║╔╗╔╗║░░░░
╚╝║║╠╩═╣║╔══╦══╦═╦══╦╗╔╦╗╔╗░░░░║╚╝╚╣║░║╠╝║║╚╝░░░░
░░║║║║═╣║║║═╣╔╗║╔╣╔╗║╚╝║╚╝║░░░░║╔═╗║║░║║░║║░░░░░░
░░║║║║═╣╚╣║═╣╚╝║║║╔╗║║║║║║║░░░░║╚═╝║╚═╝║░║║░░░░░░
░░╚╝╚══╩═╩══╩═╗╠╝╚╝╚╩╩╩╩╩╩╝░░░░╚═══╩═══╝░╚╝░░░░░░
░░░░░░░░░░░░╔═╝║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░╚══╝░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""


class Loader:

    def __init__(self):
        self.stop_flag = False

    async def start(self, static_string, animation_symbol="."):

        self.stop_flag = False
        i = 0
        while not self.stop_flag:
            print(" ", end="\r")
            print(static_string + i * animation_symbol, end="", flush=True)
            await asyncio.sleep(0.7)
            i += 1
            if i > 10:
                i = 0

    async def stop(self):
        self.stop_flag = True
        print("\r" + " "*50, end="")

    async def countdown(self, static_string, start_from=10):
        print("\r" + " "*50, end="")
        for i in range(start_from, 0, -1):
            print(" "*50, end="\r")
            print(f"{static_string}....{i}", end="", flush=True)
            await asyncio.sleep(1)
        print("\r" + " "*50, end="")
