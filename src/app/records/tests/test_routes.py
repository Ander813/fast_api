import asyncio

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


user_email = "test@mail.ru"
user_password = "12345"
user = UserIn(email=user_email, password=user_password)
token = create_token(user_email)
authorization = {"Authorization": f"Bearer {token['access_token']}"}
records = [
    RecordIn(name=f"{i}", text=f"text {i}", is_important=False if i % 2 == 1 else True)
    for i in range(5)
]

client = AsyncClient(app=app, base_url="http://test")


@pytest.fixture(autouse=True)
def initialize_tests(request):
    initializer(settings.APPS_MODELS)
    request.addfinalizer(finalizer)


async def create_user():
    return await users_s.create(user)


async def create_records(id: int):
    for i in range(len(records)):
        await records_s.create(records[i], creator_id=id)


@pytest.mark.asyncio()
async def test_post_record_unauthorized():
    response = await client.post(
        app.url_path_for("create_record"), data=records[0].json()
    )
    assert response.status_code == 401


@pytest.mark.asyncio()
async def test_post_record_authorized():
    await create_user()

    async with client as c:
        response = await c.post(
            app.url_path_for("create_record"),
            data=records[0].json(),
            headers=authorization,
        )
    assert response.status_code == 201

    json_resp = json.loads(response.content)

    assert json_resp.get("id", None)
    assert json_resp.get("name", None)
    assert json_resp.get("is_important", None) is records[0].is_important
    assert json_resp.get("create_date", None)
    assert json_resp.get("edit_date", None)


@pytest.mark.asyncio()
async def test_get_records_unauthorized():
    async with client as c:
        response = await c.get(app.url_path_for("get_records"))
    assert response.status_code == 401


@pytest.mark.asyncio()
async def test_get_records_authorized():
    await create_user()
    await create_records(id=1)

    async with client as c:
        response = await c.get(app.url_path_for("get_records"), headers=authorization)
    assert response.status_code == 200

    json_resp = json.loads(response.content)
    assert json_resp.get("items", None)
    assert type(json_resp["items"]) is list
    assert len(json_resp["items"]) == len(records)
    for key in RecordOut.__fields__:
        assert key in json_resp["items"][0]
    assert json_resp.get("total", None)
    assert json_resp.get("page", None) == 0
    assert json_resp.get("size", None)


@pytest.mark.asyncio()
async def test_get_records_with_filter_params():
    await create_user()
    await create_records(id=1)

    """Testing filter with bad order query parameter"""
    async with client as c:
        response = await c.get(
            app.url_path_for("get_records"),
            headers=authorization,
            params={"order": "bad_order"},
        )
    assert response.status_code == 400

    """Testing with -id parameter"""
    async with client as c:
        response = await c.get(
            app.url_path_for("get_records"),
            headers=authorization,
            params={"order": "-id"},
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    for i in range(len(records)):
        assert json_resp["items"][i]["id"] == len(records) - i

    """Testing with id parameter"""
    async with client as c:
        response = await c.get(
            app.url_path_for("get_records"),
            headers=authorization,
            params={"order": "id"},
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    for i in range(len(records)):
        assert json_resp["items"][i]["id"] == i + 1

    """Testing with is_important = True parameter"""
    async with client as c:
        response = await c.get(
            app.url_path_for("get_records"),
            headers=authorization,
            params={"is_important": "1"},
        )
    json_resp = json.loads(response.content)
    assert response.status_code == 200
    assert len(json_resp["items"]) == len(records) // 2 + 1
    for i in range(len(json_resp["items"])):
        assert json_resp["items"][i]["is_important"]

    """Testing with is_important = False parameter"""
    async with client as c:
        response = await c.get(
            app.url_path_for("get_records"),
            headers=authorization,
            params={"is_important": "0"},
        )
    json_resp = json.loads(response.content)
    assert response.status_code == 200
    assert len(json_resp["items"]) == len(records) // 2
    for i in range(len(json_resp["items"])):
        assert json_resp["items"][i]["is_important"] is False


# initializer(settings.APPS_MODELS)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(loop.create_task(test_get_records_with_filter_params()))
