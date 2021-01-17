import pytest
from tortoise.contrib.test import initializer, finalizer

from src.app.base.secrets import UNUSABLE_PASSWORD_PREFIX
from src.app.users.models import User
from src.conf import settings


user_email = "test@mail.ru"
user_password = "12345"


@pytest.fixture(autouse=True)
def initialize_tests(request):
    initializer(settings.APPS_MODELS)
    request.addfinalizer(finalizer)


@pytest.mark.asyncio
async def test_create_user():
    user = await User.create_user(user_email, user_password)
    assert user
    assert user.verify_password(user_password)
    assert User.get_or_none(id=1)


@pytest.mark.asyncio
async def test_create_superuser():
    superuser = await User.create_superuser(user_email, user_password)
    assert superuser
    assert superuser.superuser
    assert User.get_or_none(id=1)


@pytest.mark.asyncio
async def test_set_password():
    user = await User.create_user(user_email, user_password)
    user.set_password("test")
    await user.save()
    user = await User.get_or_none(id=1)
    assert user.verify_password("test")


@pytest.mark.asyncio
async def test_set_unusable_password():
    user = await User.create_user(user_email, user_password)
    user.set_unusable_password()
    await user.save()
    user = await User.get_or_none(id=1)
    assert user.hashed_password.startswith(UNUSABLE_PASSWORD_PREFIX)


@pytest.mark.asyncio
async def test_activate():
    user = await User.create_user(user_email, user_password)
    await user.activate()
    user = await User.get_or_none(id=1)
    assert user.activated
