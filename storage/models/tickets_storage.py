from storage.storage import StoragedList


class TicketsStorage(StoragedList):
    def __init__(self, ):
        super().__init__("tickets", filename="tickets")

    async def includes(self, ticket_id):
        return await self._includes(lambda ticket: ticket["ticketId"] == ticket_id)

    async def add(self, ticket):
        await self._add(ticket)

    async def remove(self, ticket_id):
        await self._remove(lambda ticket: ticket["ticketId"] != ticket_id)

    async def get_messages(self, ticket_id):
        tickets = await self.get_list()
        for tt in tickets:
            if tt["ticketId"] == ticket_id:
                return tt.get("messages", [])
        return []