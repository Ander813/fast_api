import pytest
from tortoise.contrib.test import initializer, finalizer

from src.app.records.models import Record
from src.app.records.schemas import RecordIn, RecordOut, RecordOutAdmin, RecordInAdmin
from src.app.records.services import records_s
from src.app.users.schemas import UserIn
from src.app.users.services import users_s

from src.conf import settings


user_email = "test@mail.ru"
user_password = "Test1234"
user = UserIn(email=user_email, password=user_password)
record_in_data = {"name": "name1", "text": "text1", "is_important": True}
record_in_admin_data = {**record_in_data, **{"creator_id": 1}}
record_out_keys = {"name", "text", "is_important", "create_date", "edit_date"}
record_out_admin_keys = {
    "name",
    "text",
    "is_important",
    "create_date",
    "edit_date",
    "creator_id",
}
record = RecordIn(**record_in_data)


async def create_user():
    return await users_s.create(user)


@pytest.fixture(autouse=True)
def initialize_tests(request):
    initializer(settings.APPS_MODELS)
    request.addfinalizer(finalizer)


async def create_record(id: int):
    await records_s.create(record, creator_id=id)


@pytest.mark.asyncio
async def test_record_in():
    for key in record_in_data.keys():
        assert key in RecordIn.__fields__
    record = RecordIn(**record_in_data).dict()
    for item in record:
        assert item


@pytest.mark.asyncio
async def test_record_out():
    await create_user()
    await create_record(id=1)

    record_obj = await Record.get(id=1)
    record = await RecordOut.from_tortoise_orm(record_obj)
    record = record.dict()
    for key in record_out_keys:
        assert key in record


@pytest.mark.asyncio
async def test_record_in_admin():
    for key in record_in_admin_data.keys():
        assert key in RecordInAdmin.__fields__
    record = RecordInAdmin(**record_in_admin_data).dict()
    for item in record:
        assert item


@pytest.mark.asyncio
async def test_record_out_admin():
    await create_user()
    await create_record(id=1)

    record_obj = await Record.get(id=1)
    record = await RecordOutAdmin.from_tortoise_orm(record_obj)
    record = record.dict()
    for key in record_out_admin_keys:
        assert key in record
