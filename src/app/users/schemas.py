from src.app.users.models import User
from tortoise.contrib.pydantic import PydanticModel
from pydantic import EmailStr


class BaseUserModel(PydanticModel):
    email: EmailStr

    class Config:
        orm_mode = True
        orig_model = User


class UserIn(BaseUserModel):
    password: str


class UserOut(BaseUserModel):
    pass


class UserInSocial(BaseUserModel):
    pass
