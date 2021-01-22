import pytest
from tortoise.contrib.test import initializer, finalizer

from src.app.users.models import User
from src.app.users.schemas import UserIn, UserOut
from src.app.users.services import users_s
from src.conf import settings


user_email = "test@mail.ru"
user_password = "12345"
user_schema = UserIn(email=user_email, password=user_password)


@pytest.fixture(autouse=True)
def initialize_tests(request):
    initializer(settings.APPS_MODELS)
    request.addfinalizer(finalizer)


@pytest.mark.asyncio
async def test_create():
    user = await users_s.create(user_schema)
    user_obj = await User.get_or_none(id=1)
    assert user_obj.verify_password(user_password)
    assert user_obj.email == user_email


@pytest.mark.asyncio
async def test_get_or_create_create():
    user, created = await users_s.get_or_create(
        defaults={"email": user_email, "password": user_password}
    )
    assert created
    assert isinstance(user, UserOut)
    user_obj = await User.get_or_none(id=1)
    assert user_obj.verify_password(user_password)
    assert user_obj.email == user_email


@pytest.mark.asyncio
async def test_get_or_create_get():
    await users_s.create(user_schema)

    user, created = await users_s.get_or_create(defaults=user_schema)
    assert not created
    assert user.email == user_email
