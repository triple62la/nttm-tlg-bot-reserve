from __future__ import annotations
import asyncio
import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload
from enum import StrEnum


class MsgTypes(StrEnum):
    ERROR_REPORT = "ERROR_REPORT"
    TICKET = "TICKET"




class Base(AsyncAttrs, DeclarativeBase):
    pass


class Settings(AsyncAttrs, DeclarativeBase):
    __tablename__ = "settings"

    key: Mapped[str]
    value: Mapped[str]


class Subscribers(Base):
    __tablename__ = "subscribers"

    chat_id: Mapped[int]
    allow_error_reports: Mapped[bool]


class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[int]
    chat_id: Mapped[int]
    type: Mapped[MsgTypes]
    ticket_id: Mapped[int]

class Tickets(Base):
    id: Mapped[int]
    isSent: Mapped[bool]


engine = create_async_engine(f"sqlite+aiosqlite:///database.db", echo=True)

