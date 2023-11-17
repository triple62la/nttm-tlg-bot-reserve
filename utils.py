import datetime
import json
import os.path
import sys
import time

import psutil
import telebot


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


def load_config():
    if "-config" in sys.argv:
        return ask_config()
    else:
        try:
            return get_config()
        except:
            if input("Файл конфигурации не найден, запустить мастера по созданию?").lower() in ["y", "yes", "у"]:
                return ask_config()
            else:
                sys.exit(0)


def get_config():
    if not os.path.exists("config.json"):
        raise Exception("Файл конфигурации не найден, положите заполненный config.json в корневую директорию!")
    else:
        with open("config.json", "r") as f:
            data = json.loads(f.read())
            if not data:
                raise Exception("Похоже что файл пуст")
            return data


def ask_config():
    config = {}
    config["nttm_url"] = input("Введите url-адрес NTTM в формате http://10.10.10.10 ")
    config["login"] = input(
        "\rВведите логин NTTM(нужен свободный логин, который не задействован в работе, иначе, бот будет отбирать у вас авторизацию в NTTM) ")
    config["password"] = input("\rВведите пароль NTTM ")
    config["polling_interval"] = int(input("\rИнтервал опроса NTTM (сек). Рекомендуется не менее 10 "))
    with open("config.json", "w") as f:
        f.write(json.dumps(config))
    return config


def get_self_pid():
    for process in psutil.process_iter():
        if process.name() == sys.argv[0].split("\\")[-1].split(".")[0] + ".exe":
            return process.pid


def check_single_instance():
    if os.path.exists("process.lock"):
        print("Вы не можете запустить несколько экземпляров приложения")
        time.sleep(5)
        sys.exit(-1)
    else:
        with open("process.lock", "w") as f:
            f.write(str(get_self_pid()))


class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        print(exception.error_code)
        if exception.error_code == 409:
            input("Похоже что запущено несколько экземпляров бота. Нажмите любую клавишу для выхода")
            sys.exit(-1)
        else:
            print(f"Был получен ошибочный ответ от телеграмм: {exception}")
        return True

