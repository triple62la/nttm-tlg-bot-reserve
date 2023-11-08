from storage.storage import StoragedList


class Subscribers(StoragedList):
    def __init__(self):
        super().__init__("subscribers", filename="subscribers")

    async def get_subscribers(self):
        return await self.get_list()

    async def add_subscriber(self, chat_id: int):
        await self._add(chat_id)

    async def remove_subscriber(self, chat_id: int):
        await self._remove(lambda item: item != chat_id)
