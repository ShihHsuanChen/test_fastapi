import uuid
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    name: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    name: Optional[str]


class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str]
