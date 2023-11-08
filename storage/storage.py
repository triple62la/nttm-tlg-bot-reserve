import json
import os.path
import aiofiles
from utils import filter


class DataStorage:

    def __init__(self, filepath=None):
        self.filepath = filepath or "./data.json"
        self._create_storage()

    def _create_storage(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode="w") as file:
                file.write(json.dumps({}))

    async def _write(self, key: str, value):
        async with aiofiles.open(self.filepath, mode="r") as file:
            data = json.loads(await file.read())
            data[key] = value
        async with aiofiles.open(self.filepath, mode="w") as file:
            await file.write(json.dumps(data))

    async def _read(self, key):
        async with aiofiles.open(self.filepath, mode="r") as file:
            return json.loads(await file.read()).get(key, None)


class StoragedList(DataStorage):
    def __init__(self, listname, filename=None):
        filepath = f"./{filename}.json" if filename else None
        super().__init__(filepath)
        self._key = listname

    async def get_list(self):
        return await self._read(self._key) or []

    async def _add(self, item):
        arr = await self.get_list() or []
        arr.append(item)
        await self._write(self._key, arr)

    async def _remove(self, callback):
        arr = await self.get_list() or []
        await self._write(self._key, filter(arr, callback))

    async def _includes(self, callback):
        arr = await self.get_list() or []
        for el in arr:
            if callback(el):
                return True
        return False
