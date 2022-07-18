from typing import Generator

from sqlalchemy import Integer, Column, VARCHAR, ForeignKey
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine


DATABASE_URL = "sqlite:///test.db?check_same_thread=False"
Base: DeclarativeMeta = declarative_base()


class User(Base):
    __tablename__ = 'user'
    uid = Column('uid', Integer, primary_key=True)
    name = Column('name', VARCHAR, nullable=True)

    def to_dict(self):
        return {'uid': self.uid, 'name': self.name}


engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(engine)


def get_local_session() -> Generator[Session, None, None]:
    with session_maker() as session:
        try:
            print('get_local_session')
            yield session
        finally:
            print('session close')
            session.close()


Base.metadata.create_all(engine)
