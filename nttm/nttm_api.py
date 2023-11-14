import asyncio

import aiohttp
from console import Loader
from nttm.nttm_exceptions import NttmAuthError, NttmFetchError, NttmNoResultsError, NttmBadResponseError, Nttm401Error, \
    AuthAttemptLimitError


class TTMApi:
    def __init__(self, login, passw, url, notification_handler, max_auth_attempts=3):
        self.login = login
        self.passw = passw
        self.payload = {
            "username": self.login,
            "password": self.passw,
            "force": "true"
        }
        self.send_notification = notification_handler
        self.url = url
        self.headers = {
            "Access-Control-Allow-Credentials": "true",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        }
        self.session = None
        self.loader = Loader()
        self.isAuthorized = False
        self.max_auth_attempts = max_auth_attempts
        self.curr_auth_attempt = 0

    async def authorize(self):
        self.curr_auth_attempt += 1
        if self.curr_auth_attempt > self.max_auth_attempts:
            raise AuthAttemptLimitError("Превышено количество попыток авторизации")

        self.session = aiohttp.ClientSession(base_url=self.url, headers=self.headers,
                                             timeout=aiohttp.ClientTimeout(connect=15))

        try:
            response = await self.session.post("/nttm-task-handler/api/authenticate", json=self.payload)
        except Exception as e:
            raise e
        else:
            if response.status >= 400:
                raise NttmAuthError(f"От сервера получен ошибочный статус код: {response.status}")
            data = await response.json()
            self.session.headers.update({'Authorization': "Bearer " + data["id_token"]})
            self.isAuthorized = True
            self.curr_auth_attempt = 0
        finally:
            await self.loader.stop()

    async def authorize_with_annonce(self):

        try:
            annonce = asyncio.create_task(self.loader.start(f"Выполняется авторизация в NTTM."
                                                            f" Попытка {self.curr_auth_attempt + 1} из {self.max_auth_attempts}"))
            auth = asyncio.create_task(self.authorize())
            await asyncio.gather(annonce, auth)
        except aiohttp.ClientConnectionError as e:
            raise Exception(f"Попытка подключения к NTTM неуспешна.Авторизация неудалась.Проверьте капсулу. {e}")
        except Exception as e:
            raise NttmAuthError(f"Попытка авторизации на {self.url} неуспешна: {e}")
        finally:
            await self.loader.stop()

    async def fetch_tickets_with_announce(self):
        try:
            async with asyncio.TaskGroup() as tg:
                annonce = tg.create_task(self.loader.start("Получение тикетов"))
                fetch = tg.create_task(self.fetch_tickets())
            return fetch.result()
        except Nttm401Error:
            await self.loader.stop()
            return []
        except aiohttp.ClientConnectionError as e:
            raise Exception(f"Попытка подключения к NTTM неуспешна.Проверьте капсулу.\n {e}")
        except Exception as e:
            raise Exception("Попытка получения тикетов неуспешна \n" + str(e))
        finally:
            await self.loader.stop()

    async def fetch_tickets(self):
        content = []

        try:
            resp = await self.session.post("/nttm-web-gateway/api/task/page?page=0&size=50&sort=id,desc", json=[])
        except Exception as e:
            raise NttmFetchError(str(e))
        else:
            if resp.status == 401:
                await self.loader.stop()
                self.isAuthorized = False
                raise Nttm401Error("От сервера пришел ответ о необходимости авторизации")

            elif resp.status != 200:
                raise NttmBadResponseError(f"От сервера NTTM пришел ошибочный код ответа:  {resp.status}")
            data = await resp.json()
            content = data.get("content", [])
            await self.loader.stop()
        finally:
            return content

    async def do_diag(self):
        return {"fetch": len(await self.fetch_tickets()) > 0, "auth": self.isAuthorized}
