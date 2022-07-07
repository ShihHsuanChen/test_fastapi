import uuid
from typing import Optional, List, Type, Generic, Generator

from sqlalchemy import select
from fastapi import Depends, Request, status, APIRouter, HTTPException
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models, schemas
from fastapi_users.exceptions import UserNotExists
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from .db import User, get_async_session, AsyncSession


SECRET = "SECRET"


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


class UserDatabase(SQLAlchemyUserDatabase):
    async def get_list(self, **kwargs):
        statement = select(self.user_table)
        for k, v in kwargs.items():
            if hasattr(self.user_table, k) and v is not None:
                statement = statement.where(getattr(self.user_table, k) == v)
        results = await self.session.execute(statement)
        return [objs[0] for objs in results.all()]


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self,
            user: User, token: str, request: Optional[Request] = None
            ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self,
            user: User, token: str, request: Optional[Request] = None
            ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def get_list(self, **kwargs):
        r"""
        get users list
        """
        if not hasattr(self.user_db, 'get_list'):
            raise NotImplementedError('method get_list is not implemented.')
        return await self.user_db.get_list(**kwargs)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield UserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


class MyFastAPIUsers(FastAPIUsers, Generic[models.UP, models.ID]):
    def get_users_router(
            self,
            user_schema: Type[schemas.U],
            user_update_schema: Type[schemas.UU],
            requires_verification: bool = False,
            ) -> APIRouter:
        """
        Return a router with routes to manage users.
        :param user_schema: Pydantic schema of a public user.
        :param user_update_schema: Pydantic schema for updating a user.
        :param requires_verification: Whether the endpoints
        require the users to be verified or not. Defaults to False.
        """
        router = super().get_users_router(
            user_schema,
            user_update_schema,
            requires_verification=requires_verification,
        )

        @router.get(
            "",
            response_model=List[user_schema],
            dependencies=[Depends(self.current_user(active=True))],
            # dependencies=[Depends(self.current_user(active=True, superuser=True))],
            name="users:list",
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                },
                status.HTTP_501_NOT_IMPLEMENTED: {
                    "description": "method not implemented",
                },
            },
        )
        async def list_users(
                is_active: Optional[bool] = None,
                is_superuser: Optional[bool] = None,
                is_verified: Optional[bool] = None,
                user_manager: BaseUserManager[models.UP, models.ID] = Depends(self.get_user_manager)
                ):
            if not hasattr(user_manager, 'get_list'):
                raise HTTPException(501)
            users = await user_manager.get_list(
                is_active=is_active,
                is_superuser=is_superuser,
                is_verified=is_verified,
            )
            return users
        return router


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)

fastapi_users = MyFastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

get_current_user = fastapi_users.current_user(active=True)


async def get_user(
        user_id: str,
        user_manager = Depends(get_user_manager),
        ) -> Generator[str, None, None]:
    try:
        other = await user_manager.get(user_id)
    except UserNotExists:
        raise HTTPException(404, 'User not exists')
    except Exception:
        raise HTTPException(404, 'Invalid user_id format')
    yield other
