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
        await asyncio.sleep(0.1)
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
    assert records_s.get_obj(id=len(records) + 1)

    json_resp = json.loads(response.content)
    for key in RecordOut.__fields__:
        assert key in json_resp


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
    for key in Page.__fields__:
        assert key in json_resp
    assert len(json_resp["items"]) == len(records)
    for key in RecordOut.__fields__:
        assert key in json_resp["items"][0]


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

    """Testing with -id order parameter"""
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

    """Testing with id order parameter"""
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

    """Testing with is_important + order parameters"""
    async with client as c:
        response = await c.get(
            app.url_path_for("get_records"),
            headers=authorization,
            params={"is_important": "1", "order": "id"},
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    assert len(json_resp["items"]) == len(records) // 2 + 1
    for i in range(len(json_resp["items"]) - 1):
        assert json_resp["items"][i]["id"] < json_resp["items"][i + 1]["id"]

    """Testing with date_from = now() => expecting 0 items"""
    async with client as c:
        response = await c.get(
            app.url_path_for("get_records"),
            headers=authorization,
            params={"date_from": datetime.now()},
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    assert len(json_resp["items"]) == 0

    """Testing with date_to = 3rd record creation time"""
    record = await records_s.get(id=3)
    time_created = record.create_date
    async with client as c:
        response = await c.get(
            app.url_path_for("get_records"),
            headers=authorization,
            params={"date_to": time_created},
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    assert len(json_resp["items"]) == 3


@pytest.mark.asyncio()
async def test_get_record_unauthorized():
    async with client as c:
        response = await c.get(app.url_path_for("get_record", id="1"))
    assert response.status_code == 401


@pytest.mark.asyncio()
async def test_get_record_authorized_with_bad_id():
    await create_user()

    async with client as c:
        response = await c.get(
            app.url_path_for("get_record", id="bad_id"), headers=authorization
        )
    assert response.status_code == 422


@pytest.mark.asyncio()
async def test_get_record_authorized_with_wrong_id():
    await create_user()

    async with client as c:
        response = await c.get(
            app.url_path_for("get_record", id=len(records) + 1), headers=authorization
        )
    assert response.status_code == 404


@pytest.mark.asyncio()
async def test_get_record_authorized():
    await create_user()
    await create_records(id=1)

    async with client as c:
        response = await c.get(
            app.url_path_for("get_record", id=1), headers=authorization
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    for key in RecordOut.__fields__:
        assert key in json_resp
    assert json_resp["id"] == 1


@pytest.mark.asyncio()
async def test_update_record_unauthorized():
    async with client as c:
        response = await c.put(
            app.url_path_for("update_record", id=1), data=records[1].json()
        )
    assert response.status_code == 401


@pytest.mark.asyncio()
async def test_update_record_authorized_with_bad_id():
    await create_user()

    async with client as c:
        response = await c.put(
            app.url_path_for("update_record", id="bad_id"),
            data=records[1].json(),
            headers=authorization,
        )
    assert response.status_code == 422


@pytest.mark.asyncio()
async def test_update_record_authorized_with_wrong_id():
    await create_user()

    async with client as c:
        response = await c.put(
            app.url_path_for("update_record", id=len(records) + 1),
            data=records[1].json(),
            headers=authorization,
        )
    assert response.status_code == 404


@pytest.mark.asyncio()
async def test_update_record_authorized():
    await create_user()
    await create_records(id=1)

    async with client as c:
        response = await c.put(
            app.url_path_for("update_record", id=1),
            data=records[1].json(),
            headers=authorization,
        )
    assert response.status_code == 200
    json_resp = json.loads(response.content)
    for key in RecordOut.__fields__:
        assert key in json_resp
    for key in RecordIn.__fields__:
        assert json_resp[key] == records[1].dict()[key]


@pytest.mark.asyncio()
async def test_delete_record_unauthorized():
    async with client as c:
        response = await c.delete(app.url_path_for("delete_record", id=1))
    assert response.status_code == 401


@pytest.mark.asyncio()
async def test_delete_record_authorized_with_bad_id():
    await create_user()

    async with client as c:
        response = await c.delete(
            app.url_path_for("delete_record", id="bad_id"), headers=authorization
        )
    assert response.status_code == 422


@pytest.mark.asyncio()
async def test_delete_record_authorized_with_wrong_id():
    await create_user()

    async with client as c:
        response = await c.delete(
            app.url_path_for("delete_record", id=len(records) + 1),
            headers=authorization,
        )
    assert response.status_code == 404


@pytest.mark.asyncio()
async def test_delete_record_authorized():
    await create_user()
    await create_records(id=1)

    async with client as c:
        response = await c.delete(
            app.url_path_for("delete_record", id=1),
            headers=authorization,
        )
    assert response.status_code == 200
    records_in_db = await records_s.all()
    assert len(records_in_db) == len(records) - 1
    assert await records_s.filter(id=1) == []


# initializer(settings.APPS_MODELS)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(loop.create_task(test_get_records_with_filter_params()))
