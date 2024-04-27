import asyncio
import sqlalchemy.engine
from database.types import DbExecResult, ExecStatus
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import engine, Subscribers, Tickets, Messages
from typing import List, Literal, Optional
import sqlalchemy.exc






async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def add_subscriber(chat_id: int, allow_reports=True) -> DbExecResult:
    async with async_session() as session:
        try:
            sub = Subscribers(chat_id=chat_id, allow_error_reports=allow_reports)
            session.add(sub)
            await session.commit()
            return {"status": ExecStatus.SUCCESS, "message": None, "error": None}
        except sqlalchemy.exc.IntegrityError as e:
            return {"status": ExecStatus.ERROR, "message": f"Пользователь с таким ID уже существует. {e}", "error": e}
        except Exception as e:
            return {"status": ExecStatus.ERROR, "message": f"Ошибка добавления нового подписчика. {e}", "error": e}

async def get_subscribers() -> List[Subscribers]:
    async with async_session() as session:
        result = await session.execute(select(Subscribers))
        return result.scalars().all()


async def remove_sub_by_id(chat_id: int) -> DbExecResult:
    async with async_session() as session:
        try:
            await session.execute(delete(Subscribers).where(Subscribers.chat_id == chat_id))
            await session.commit()
            return {"status": ExecStatus.SUCCESS, "message": None, "error": None}
        except Exception as e:
            session.rollback()
            return {"status": ExecStatus.ERROR, "message": f"Ошибка удаления нового подписчика. {e}", "error": e}

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

async def add_msg_to_db():
    async with async_session() as session:
        msg = Messages()
        await session.execute()


if __name__ == "__main__":
    async def main():
        print(await add_subscriber(123456))
        for sub in await get_subscribers():
            print(sub.chat_id)



    asyncio.run(main())
