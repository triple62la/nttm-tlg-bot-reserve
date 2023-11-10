import asyncio

import aiohttp
from console import Loader


class NoResultsException(Exception):
    pass


class TTMApi:
    def __init__(self, login, passw, url, notification_handler):
        self.login = login
        self.passw = passw
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

    async def authorize(self):

        self.session = aiohttp.ClientSession(base_url=self.url, headers=self.headers,
                                             timeout=aiohttp.ClientTimeout(connect=15))
        payload = {
            "username": self.login,
            "password": self.passw,
            "force": "true"
        }
        async with self.session.post("/nttm-task-handler/api/authenticate", json=payload) as response:
            data = await response.json()
            self.session.headers.update({'Authorization': "Bearer " + data["id_token"]})
            self.isAuthorized = True
        await self.loader.stop()

    async def authorize_with_annonce(self):
        try:
            annonce = asyncio.create_task(self.loader.start("Выполняется авторизаци в NTTM"))
            auth = asyncio.create_task(self.authorize())
            await asyncio.gather(annonce, auth)
        except Exception as e:
            raise Exception(f"Попытка авторизации на {self.url} неуспешна: {e}")
        finally:
            await self.loader.stop()

    async def fetch_tickets_with_announce(self):
        try:
            async with asyncio.TaskGroup() as tg:
                annonce = tg.create_task(self.loader.start("Получение тикетов"))
                fetch = tg.create_task(self.fetch_tickets())
            return fetch.result()
        except Exception as e:
            raise Exception("Попытка получения тикетов неуспешна \n" + str(e))
        finally:
            await self.loader.stop()

    async def fetch_tickets(self):

        async with self.session.post("/nttm-web-gateway/api/task/page?page=0&size=50&sort=id,desc",
                                     json=[]) as resp:
            if resp.status == 401:
                await self.loader.stop()
                self.isAuthorized = False
                await self.authorize_with_annonce()
                return []
            data = await resp.json()
            content = data.get("content", [])
            if not content: raise Exception("В ответе NTTM отсутствуют результаты")
            await self.loader.stop()
            return content
