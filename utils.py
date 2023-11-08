import asyncio
import datetime
import json
import os.path
import sys


def find(arr, callback):
    for item in arr:
        if callback(item):
            return item


def find_index(arr: list, callback):
    for item, index in enumerate(arr):
        if callback(item):
            return index


def find_tt(arr, ticketId: int):
    for item in arr:
        if item["ticketId"] == ticketId:
            return item
    return


def filter(arr, callback):
    results = []
    for item in arr:
        if callback(item):
            results.append(item)
    return results


def save_err_log(error: Exception):
    now = datetime.datetime.now()
    filename = now.strftime("%d-%m-%y--%H-%M-%S")
    with open(filename, "w") as f:
        f.write(str(error))


def filter_indexes(arr, callback):
    results = []
    for item, index in enumerate(arr):
        if callback(item):
            results.append(index)
    return results


class Loader:

    def __init__(self):
        self.stop_flag = False

    async def start(self):
        self.stop_flag = False
        string = ""
        while not self.stop_flag:
            await asyncio.sleep(0.7)
            sys.stdout.flush()
            string += "."
            sys.stdout.write("\r" + string)
            if len(string) > 10:
                string = ""

    async def stop(self):
        self.stop_flag = True


def get_config():
    if not os.path.exists("config.json"):
        raise Exception("Файл конфигурации не найден, положите заполненный config.json в корневую директорию!")
    else:
        with open("config.json", "r") as f:
            data = json.loads(f.read())
            if not data:
                raise Exception("Похоже что файл пуст")
            return data
