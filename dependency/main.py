from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Query

from db import get_local_session, session_maker, User


class Manager:
    def __init__(self, session: Session):
        self.session = session

    def get_user(self, user_id: int):
        try:
            user = self.session.query(User).filter_by(uid=user_id).one()
        finally:
            self.session.rollback()
        return user

    def ss(self, user: User):
        return f'{user.name}={user.uid}'


app = FastAPI()


async def get_manager(session: Session = Depends(get_local_session)):
    print('get manager')
    yield Manager(session)


@app.post('/bbb')
def create_bbb(
        session: Session = Depends(get_local_session),
        ):
    try:
        user = User()
        session.add(user)
        session.commit()
    finally:
        session.rollback()
    return user.to_dict()


def get_user(
        user_id: int,
        session: Session = Depends(get_local_session),
        ):
    try:
        user = session.query(User).filter_by(uid=user_id).one()
    finally:
        session.rollback()
    yield user


def get_user_from_manager(
        user_id: int,
        manager: Manager = Depends(get_manager),
        ):
    yield manager.get_user(user_id)


@app.get('/bbb')
def get_bbb(
        user: User = Depends(get_user),
        ):
    return user.to_dict()


@app.get('/aaa')
def get_aaa(
        user: User = Depends(get_user_from_manager),
        manager: Manager = Depends(get_manager),
        ):
    return manager.ss(user)
