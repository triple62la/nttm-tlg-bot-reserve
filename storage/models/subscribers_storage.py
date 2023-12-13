from storage.storage import StoragedList


class Subscribers(StoragedList):
    def __init__(self):
        super().__init__("subscribers", filename="subscribers")

    async def get_subscribers(self):
        return await self.get_list()

    async def add_subscriber(self, chat_id: int, allow_reports=False):
        await self._add({"chat_id": chat_id, "allow_reports": allow_reports})

    async def remove_subscriber(self, chat_id: int):
        await self._remove(lambda item: item != chat_id)

    async def set_allow_reports(self, chat_id: int, value: bool):
        await self._change_item(lambda item: item["chat_id"] == chat_id, {"chat_id": chat_id, "allow_reports": value})
