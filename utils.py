import datetime
import json
import os.path


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
        "\rВведите логин NTTM(нужен свободный логин, который не задействован в работе, иначе, будет перебивать авторизацию) ")
    config["password"] = input("\rВведите пароль NTTM " + " "*65)
    config["polling_interval"] = int(input("\rИнтервал опроса NTTM (сек). Рекомендуется не менее 10 "))
    with open("config.json", "w") as f:
        f.write(json.dumps(config))
    return config
