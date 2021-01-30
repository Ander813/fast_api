import asyncio
import json

import pytest
from httpx import AsyncClient
from passlib.context import CryptContext
from tortoise.contrib.test import initializer, finalizer

from src.app.auth.tasks import email_prefix, confirm_prefix, reset_prefix
from src.app.base.redis import Redis
from src.app.users.models import User
from testing_main import app
from src.app.auth.jwt import create_token
from src.app.users.schemas import UserIn
from src.app.users.services import users_s
from src.conf import settings


user_email = "test@mail.ru"
user_password = "Test1234"
user = UserIn(email=user_email, password=user_password)
token = create_token(user_email)
refresh_token = create_token(user_email, refresh=True)["refresh_token"]
wrong_refresh_token = create_token("wrong_email@mail.ru", refresh=True)["refresh_token"]
authorization = {"Authorization": f"Bearer {token['access_token']}"}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

client = AsyncClient(app=app, base_url="http://test")


async def create_user():
    return await users_s.create(user, activated=True)


@pytest.fixture(autouse=True)
def initialize_tests(request):
    initializer(settings.APPS_MODELS)
    request.addfinalizer(finalizer)


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_user_registration():
    async with client as c:
        response = await c.post(app.url_path_for("user_registration"), data=user.json())
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    assert json_resp["msg"] == "successfully registered"
    user_obj = await User.get(email=user_email)
    assert user_obj.verify_password(user_password)
    assert user_obj.email == user_email


@pytest.mark.asyncio
async def test_user_registration_with_bad_email():
    async with client as c:
        response = await c.post(
            app.url_path_for("user_registration"),
            data='"email": bad_email, "password": 12345',
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_registration_with_existing_email():
    await create_user()

    async with client as c:
        response = await c.post(
            app.url_path_for("user_registration"),
            data=user.json(),
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_user_registration_confirm():
    await create_user()

    redis_instance = await Redis(
        host=settings.REDIS_HOST, password=settings.REDIS_PASSWORD, db=settings.REDIS_DB
    ).get_instance()
    _, keys = await redis_instance.scan(match=f"{email_prefix}:{confirm_prefix}:*")
    uuid = keys[0].decode("utf-8").split(":")[-1]

    async with client as c:
        response = await c.get(app.url_path_for("user_registration_confirm", uuid=uuid))
    assert response.status_code == 200
    assert (await User.get(id=1)).activated


@pytest.mark.asyncio
async def test_user_registration_confirm_with_bad_uuid():
    async with client as c:
        response = await c.get(
            app.url_path_for("user_registration_confirm", uuid="bad_uuid")
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_user_token_refresh_without_cookie():
    await create_user()

    async with client as c:
        response = await c.post(
            app.url_path_for("user_token_refresh"),
            headers=authorization,
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_token_refresh_without_authorization_header():
    await create_user()

    async with client as c:
        response = await c.post(
            app.url_path_for("user_token_refresh"),
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_token_refresh_with_wrong_refresh_token():
    await create_user()

    async with client as c:
        response = await c.post(
            app.url_path_for("user_token_refresh"),
            cookies={"refresh_token": wrong_refresh_token},
            headers=authorization,
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_token_refresh():
    await create_user()

    async with client as c:
        response = await c.post(
            app.url_path_for("user_token_refresh"),
            cookies={"refresh_token": refresh_token},
            headers=authorization,
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_user_token_login():
    await create_user()

    async with client as c:
        response = await c.post(
            app.url_path_for("user_token_login"),
            data={"username": user_email, "password": user_password},
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    assert json_resp["access_token"]
    assert json_resp["token_type"] == "bearer"
    assert response.cookies.get("refresh_token")


@pytest.mark.asyncio
async def test_user_token_login_with_wrong_credentials():
    async with client as c:
        response = await c.post(
            app.url_path_for("user_token_login"),
            data={"username": "wrong_email", "password": "wrong_password"},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_user_recover_password():
    await create_user()

    async with client as c:
        response = await c.post(
            app.url_path_for("user_recover_password"), json={"email": user_email}
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    assert json_resp["msg"]


@pytest.mark.asyncio
async def test_user_recover_password_with_wrong_email():
    async with client as c:
        response = await c.post(
            app.url_path_for("user_recover_password"), json={"email": "wrong_email"}
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reset_password():
    await create_user()

    redis_instance = await Redis(
        host=settings.REDIS_HOST, password=settings.REDIS_PASSWORD, db=settings.REDIS_DB
    ).get_instance()
    _, keys = await redis_instance.scan(match=f"{email_prefix}:{reset_prefix}:*")
    uuid = keys[0].decode("utf-8").split(":")[-1]

    async with client as c:
        response = await c.post(
            app.url_path_for("reset_password"),
            json={"uuid": uuid, "password": "New_password1"},
        )
    assert response.status_code == 200
    user_obj = await User.get(id=1)
    assert user_obj.verify_password("New_password1")


@pytest.mark.asyncio
async def test_reset_password_with_wrong_uuid():
    async with client as c:
        response = await c.post(
            app.url_path_for("reset_password"),
            json={"uuid": "wrong_uuid", "password": "New_password1"},
        )
    assert response.status_code == 400
