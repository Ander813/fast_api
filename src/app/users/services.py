from src.app.base.services import BaseService
from . import schemas
from .models import User


class UsersService(BaseService):
    model = User
    create_schema = schemas.UserIn
    update_schema = schemas.UserIn
    get_schema = schemas.UserOut

    async def create_user(self, schema):
        user_obj = await self.model.create_user(**schema.dict())
        return await self.get_schema.from_tortoise_orm(user_obj)


users_s = UsersService()
