import pytest
from tortoise.contrib.test import initializer, finalizer

from src.app.users.models import User
from src.app.users.schemas import UserIn, UserOut, UserInSocial
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


@pytest.mark.asyncio
async def test_create_superuser():
    await users_s.create_superuser(user_schema)

    user = await User.get_or_none(id=1)
    assert user
    assert user.verify_password(user_password)
    assert user.superuser


@pytest.mark.asyncio
async def test_create_social():
    await users_s.create_social(UserInSocial(email=user_email))

    user = await User.get_or_none(id=1)
    assert user
    assert not user.if_password_usable()


@pytest.mark.asyncio
async def test_get_or_create_social_create():
    user, created = await users_s.get_or_create_social(
        UserInSocial(email=user_email), email=user_email
    )

    assert isinstance(user, UserOut)
    assert created
    user_obj = await User.get_or_none(id=1)
    assert user_obj
    assert not user_obj.if_password_usable()


@pytest.mark.asyncio
async def test_get_or_create_social_get():
    await users_s.create_social(UserInSocial(email=user_email))

    user, created = await users_s.get_or_create_social(
        UserInSocial(email=user_email), email=user_email
    )

    assert isinstance(user, UserOut)
    assert not created
    user_obj = await User.get_or_none(id=1)
    assert user_obj
    assert not user_obj.if_password_usable()


@pytest.mark.asyncio
async def test_authenticate_with_wrong_credentials():
    assert not await users_s.authenticate("wrong_email@mail.ru", "wrong_password")


@pytest.mark.asyncio
async def test_authenticate():
    await users_s.create(user_schema)
    assert await users_s.authenticate(user_email, user_password)


@pytest.mark.asyncio
async def test_set_password():
    await users_s.create(user_schema)
    await users_s.set_password("test1234", id=1)

    user_obj = await User.get_or_none(id=1)
    assert user_obj.verify_password("test1234")
