import asyncio
from datetime import datetime

from fastapi_pagination import Page
from httpx import AsyncClient
from tortoise.contrib.test import initializer, finalizer

from src.app.auth.jwt import create_token
from src.app.records.schemas import RecordIn, RecordOut
from src.app.records.services import records_s
from src.app.users.schemas import UserIn
from src.app.users.services import users_s
from src.conf import settings
from testing_main import app
import json
import pytest


superuser_email, user_email = "test@mail.ru", "test2@mail.ru"
superuser_password = user_password = "12345"
superuser = UserIn(email=superuser_email, password=superuser_password)
user = UserIn(email=user_email, password=user_password)
superuser_token = create_token(superuser_email)
user_token = create_token(user_email)
superuser_authorization = {"Authorization": f"Bearer {superuser_token['access_token']}"}
user_authorization = {"Authorization": f"Bearer {user_token['access_token']}"}
records = [
    RecordIn(name=f"{i}", text=f"text {i}", is_important=False if i % 2 == 1 else True)
    for i in range(5)
]

client = AsyncClient(app=app, base_url="http://test")


@pytest.fixture(autouse=True)
def initialize_tests(request):
    initializer(settings.APPS_MODELS)
    request.addfinalizer(finalizer)


async def create_superuser():
    return await users_s.create_superuser(superuser)


async def create_user():
    return await users_s.create(user)


async def create_records(id: int):
    for i in range(len(records)):
        await asyncio.sleep(0.1)
        await records_s.create(records[i], creator_id=id)


@pytest.mark.asyncio
async def test_get_records_unauthorized():
    async with client as c:
        response = await c.get(app.url_path_for("admin_get_records"))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_records_with_common_user():
    await create_user()

    async with client as c:
        response = await c.get(
            app.url_path_for("admin_get_records"), headers=user_authorization
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_records_with_superuser():
    await create_superuser()
    await create_user()
    await create_records(id=1)
    await create_records(id=2)

    async with client as c:
        response = await c.get(
            app.url_path_for("admin_get_records"), headers=superuser_authorization
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    for key in Page.__fields__:
        assert key in json_resp
    assert len(json_resp["items"]) == 2 * len(records)
