from storage.storage import StoragedList


class ReportsStorage(StoragedList):
    def __init__(self):
        super().__init__("reports", filename="reports")

    async def add(self, msg):
        await self._add(msg)

    async def reset(self):
        await self._reset()
