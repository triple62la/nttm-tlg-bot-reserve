from utils import find_index
import aiohttp


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

    async def authorize(self):
        try:
            self.session = aiohttp.ClientSession(base_url=self.url, headers=self.headers)
            payload = {
                "username": self.login,
                "password": self.passw,
                "force": "true"
            }
            async with self.session.post("/nttm-task-handler/api/authenticate", json=payload) as response:
                try:
                    data = await response.json()
                    self.session.headers.update({'Authorization': "Bearer " + data["id_token"]})
                except aiohttp.ClientConnectorError:
                    await self.send_notification("Проблема с подключением к NTTM ")
                except aiohttp.ContentTypeError:
                    await self.send_notification("Attempt to decode JSON with unexpected mimetype", response.text)
        except aiohttp.ClientConnectorError:
            self.send_notification("Проблема с подключением к NTTM ")

    async def fetch_tickets(self):

        async with self.session.post("/nttm-web-gateway/api/task/page?page=0&size=50&sort=id,desc", json=[]) as resp:
            try:
                if resp.status == 401:
                    await self.authorize()
                    return []
                data = await resp.json()
                content = data.get("content", [])
                if not content: raise NoResultsException
                return content
            except aiohttp.ClientConnectorError:
                await self.send_notification("Проблема с подключением к NTTM ")
                return []
            except NoResultsException:
                await self.send_notification("В ответе NTTM отсутствуют результаты")
