from typing import Union, Optional

from tortoise.exceptions import DoesNotExist

from src.app.base.services import BaseService, CreateSchemaType
from . import schemas
from .models import User


class UsersService(BaseService):
    model = User
    create_schema = schemas.UserIn
    update_schema = schemas.UserIn
    get_schema = schemas.UserOut

    async def create(self, schema, **kwargs):
        user_obj = await self.model.create_user(**schema.dict(), **kwargs)
        return await self.get_schema.from_tortoise_orm(user_obj)

    async def get_or_create(self, defaults: Union[dict, CreateSchemaType], **kwargs):
        if isinstance(defaults, dict):
            defaults = self.create_schema(**defaults)
        user_obj = await self.model.get_or_none(**kwargs, email=defaults.email)
        if user_obj:
            return await self.get_schema.from_tortoise_orm(user_obj), False
        return await self.create(defaults), True

    async def create_superuser(self, schema):
        user_obj = await self.model.create_superuser(**schema.dict())
        return await self.get_schema.from_tortoise_orm(user_obj)

    async def create_social(self, schema):
        user_obj = await self.model.create_social_user(**schema.dict())
        return await self.get_schema.from_tortoise_orm(user_obj)

    async def get_or_create_social(self, defaults, **kwargs):
        user_obj = await self.model.filter(**kwargs).first()
        if user_obj:
            return await self.get_schema.from_tortoise_orm(user_obj), False
        return await self.create_social(defaults), True

    async def authenticate(self, email: str, password: str) -> Union[User, None]:
        try:
            user = await self.model.get(email=email)
        except DoesNotExist:
            return None
        if not user.verify_password(password):
            return None
        return user

    async def set_password(self, password: str, user: Optional[User] = None, **kwargs):
        if not user:
            user = await self.model.get(**kwargs)
        user.set_password(password)
        await user.save()


class UsersServiceAdmin(UsersService):
    get_schema = schemas.UserOutAdmin


users_s = UsersService()
users_s_admin = UsersServiceAdmin()
