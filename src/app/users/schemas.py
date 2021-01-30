import re

from src.app.users.models import User
from tortoise.contrib.pydantic import PydanticModel
from pydantic import EmailStr, Field, validator


class BaseUserModel(PydanticModel):
    email: EmailStr

    class Config:
        orm_mode = True
        orig_model = User


class PasswordSchema(PydanticModel):
    password: str = Field(..., min_length=8)

    @validator("password")
    def valid_password(cls, v):
        assert re.search(r"[a-z]+", v), "Must have at least one lower case letter"
        assert re.search(r"[A-Z]+", v), "Must have at least one upper case letter"
        assert re.search(r"[1-9]+", v), "Must have at least one number"
        assert not re.search(
            r"[^a-zA-Z1-9_]+", v
        ), "Only letters, numbers and _ are allowed"
        return v


class ResetPasswordSchema(PasswordSchema):
    uuid: str


class UserIn(BaseUserModel, PasswordSchema):
    pass


class UserOut(BaseUserModel):
    pass


class UserInSocial(BaseUserModel):
    pass


class UserInAdmin(UserIn):
    activated: bool = Field(False)
    superuser: bool = Field(False)


class UserOutAdmin(BaseUserModel):
    id: int
    activated: bool
    superuser: bool
