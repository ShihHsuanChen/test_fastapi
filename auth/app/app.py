from typing import Optional, List
from functools import partial
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi_users.exceptions import UserNotExists

from .db import User, async_create_db_and_tables, Data, get_local_session, Session, create_admin_user, DATABASE_URL
from .schemas import UserCreate, UserRead, UserUpdate
from .users import auth_backend, get_current_user, fastapi_users, get_user
from .rbac import InstanceGroupPolicy


import casbin
import casbin_sqlalchemy_adapter

adapter = casbin_sqlalchemy_adapter.Adapter(DATABASE_URL)
enforcer = casbin.Enforcer('./app/rbac_model.conf', adapter)


app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.email}!"}


data_policy = InstanceGroupPolicy(
    enforcer,
    'data',
    # resource_key='uid',
    can_assign_owner=True,
    default_role='edit',
)


check_permission = partial(data_policy.check_permission, get_current_user)

@app.post("/data")
async def create_data(
        name: str,
        session: Session = Depends(get_local_session),
        user: User = Depends(get_current_user),
        ):
    try:
        obj = Data(name=name)
        session.add(obj)
        session.commit()
    finally:
        session.rollback()
    data_policy.add_permission(user, obj.uid)
    return obj.to_dict()


@app.get("/data")
async def get_data_list(
        session: Session = Depends(get_local_session),
        user: User = Depends(get_current_user),
        ):
    objs = session.query(Data).all()
    res = [
        obj.to_dict() for obj in objs
        if data_policy.has_permission(user, obj.uid)
    ]
    return res


@app.get("/data/{uid}")
async def get_data(
        uid: int = Depends(check_permission('read')),
        session: Session = Depends(get_local_session),
        ):
    data = session.query(Data).filter_by(uid=uid).one()
    return data.to_dict()


@app.patch("/data/{uid}")
async def update_data(
        uid: int = Depends(check_permission('write')),
        name: Optional[str] = None,
        session: Session = Depends(get_local_session),
        ):
    try:
        obj = session.query(Data).filter_by(uid=uid).one()
        if name is not None:
            obj.name = name
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.rollback()
    return obj.to_dict()


@app.delete("/data/{uid}")
async def delete_data(
        uid: int = Depends(check_permission('write')),
        session: Session = Depends(get_local_session),
        ):
    try:
        session.query(Data).filter_by(uid=uid).delete()
        session.commit()
    except Exception as e:
        print(e)
        return False
    finally:
        session.rollback()
    return True


app.include_router(
    data_policy.get_router(
        get_current_user,
        get_user,
        instance_path='/{uid}',
    ),
    prefix='/data',
)


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await async_create_db_and_tables()
    create_admin_user(email='admin@example.com', password='admin')
