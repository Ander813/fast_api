from pydantic import validator
import re
from src.app.users.models import User
from tortoise.contrib.pydantic import PydanticModel


class BaseUserModel(PydanticModel):
    username: str
    email: str

    class Config:
        orm_mode = True
        orig_model = User

class UserIn(BaseUserModel):
    password: str

    @validator('email')
    def validate_email(cls, v):
        if re.match(r'[^@]+@[^@]+\.[^@]+', v):
            return v
        else:
            raise ValueError('Not email')


class UserOut(BaseUserModel):
    pass

