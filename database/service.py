import sqlalchemy.engine
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.sqlite import Insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import engine, Subscribers, Tickets, Messages

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_subscribers():
    async with async_session() as session:
        result = await session.execute(select(Subscribers))
        return result.scalars().all()


async def remove_sub_by_id(chat_id):
    async with async_session() as session:
        await session.execute(delete(Subscribers).where(Subscribers.chat_id == chat_id))
        await session.commit()


async def get_ticket_by_id(ticket_id):
    async with async_session() as session:
        result = await session.execute(select(Tickets).where(Tickets.id == ticket_id))
        return await result.scalars().one_or_none()


async def remove_ticket_by_id(ticket_id):
    async with async_session() as session:
        await session.execute(delete(Tickets).where(Tickets.id == ticket_id))
        await session.commit()


async def get_msgs_by_ticket_id(ticket_id):
    async with async_session() as session:
        result = await session.execute(select(Messages).where(Messages.ticket_id == ticket_id))
        return result.scalars().all()


async def del_msgs_by_ticket_id(ticket_id):
    async with async_session() as session:
        await session.execute(delete(Tickets).where(Tickets.id == ticket_id))
        await session.commit()
