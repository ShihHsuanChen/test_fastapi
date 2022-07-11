from typing import AsyncGenerator, Generator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
# from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, Column, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine


DATABASE_URL_ASYNC = "sqlite+aiosqlite:///./test.db"
DATABASE_URL = "sqlite:///./test.db?check_same_thread=False"
Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    name = Column('name', VARCHAR, nullable=True)


class Data(Base):
    __tablename__ = 'data'
    uid = Column('uid', Integer, primary_key=True)
    name = Column('name', VARCHAR, nullable=True)

    def to_dict(self):
        return {'uid': self.uid, 'name': self.name}


async_engine = create_async_engine(DATABASE_URL_ASYNC)
async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(engine)

def create_db_and_tables():
    Base.metadata.create_all(engine)


def get_local_session() -> Generator[Session, None, None]:
    with session_maker() as session:
        try:
            yield session
        finally:
            session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def create_admin_user(**kwargs):
    from fastapi_users.password import PasswordHelper

    kwargs['hashed_password'] = PasswordHelper().hash(kwargs.pop('password'))
    with session_maker() as session:
        try:
            session.add(User(**kwargs, is_superuser=True))
            session.commit()
        except Exception as e:
            pass
        finally:
            session.rollback()
            session.close()
