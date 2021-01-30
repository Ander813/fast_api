import asyncio

import pytest
from tortoise.contrib.test import initializer, finalizer
from tortoise.exceptions import DoesNotExist

from src.app.records.filters import RecordFilter
from src.app.records.models import Record
from src.app.records.schemas import RecordIn, RecordOut
from src.app.records.services import records_s
from src.app.users.schemas import UserIn
from src.app.users.services import users_s
from src.conf import settings


user_email = "test@mail.ru"
user_password = "Test1234"
user = UserIn(email=user_email, password=user_password)
record_in_data = {"name": "name1", "text": "text1", "is_important": True}
record_update_data = {
    "name": "updated name",
    "text": "updated text",
    "is_important": True,
}
record = RecordIn(**record_in_data)
update_record = RecordIn(**record_update_data)
records = [
    RecordIn(name=f"{i}", text=f"text {i}", is_important=False if i % 2 == 1 else True)
    for i in range(5)
]


async def create_user():
    return await users_s.create(user)


@pytest.fixture(autouse=True)
def initialize_tests(request):
    initializer(settings.APPS_MODELS)
    request.addfinalizer(finalizer)


async def create_record(id: int):
    await records_s.create(record, creator_id=id)


async def create_records(id: int):
    for i in range(len(records)):
        await asyncio.sleep(0.1)
        await records_s.create(records[i], creator_id=id)


@pytest.mark.asyncio
async def test_create():
    await create_user()

    record_schema = await records_s.create(record, creator_id=1)
    assert isinstance(record_schema, RecordOut)
    record_obj = await Record.get_or_none(id=1)
    assert record_obj
    for key in record_in_data.keys():
        assert getattr(record_obj, key) == record_in_data[key]


@pytest.mark.asyncio
async def test_update_with_wrong_id():
    await create_user()
    await create_record(id=1)

    try:
        await records_s.update(update_record, id=2, creator_id=1)
    except DoesNotExist:
        pass


@pytest.mark.asyncio
async def test_update():
    await create_user()
    await create_record(id=1)

    record_schema = await records_s.update(update_record, id=1, creator_id=1)
    assert isinstance(record_schema, RecordOut)
    record_obj = await Record.get_or_none(id=1)
    assert record_obj
    for key in record_update_data.keys():
        assert getattr(record_obj, key) == record_update_data[key]


@pytest.mark.asyncio
async def test_delete_with_wrong_id():
    await create_user()
    await create_record(id=1)

    deleted_record = await records_s.delete(id=2)
    assert deleted_record == 0


@pytest.mark.asyncio
async def test_delete():
    await create_user()
    await create_record(id=1)

    deleted_record = await records_s.delete(id=1)
    assert deleted_record == 1
    assert await Record.get_or_none(id=1) is None


@pytest.mark.asyncio
async def test_get_with_wrong_id():
    await create_user()
    await create_record(id=1)

    try:
        await records_s.get(id=2)
    except DoesNotExist:
        pass


@pytest.mark.asyncio
async def test_get():
    await create_user()
    await create_record(id=1)

    record_schema = await records_s.get(id=1)
    assert isinstance(record_schema, RecordOut)
    for key in record_in_data.keys():
        assert getattr(record_schema, key) == record_in_data[key]


@pytest.mark.asyncio
async def test_all():
    await create_user()
    await create_records(id=1)

    record_schemas_list = await records_s.all()
    assert isinstance(record_schemas_list, list)
    for i in range(len(record_schemas_list)):
        assert isinstance(record_schemas_list[i], RecordOut)
    for i in range(len(record_schemas_list)):
        for key in record_in_data.keys():
            assert getattr(record_schemas_list[i], key) == getattr(
                records[len(records) - 1 - i], key
            )


@pytest.mark.asyncio
async def test_filter_with_wrong_parameter():
    await create_user()
    await create_records(id=1)

    filtered_record_schemas_list = await records_s.filter(name="non-existing name")
    assert filtered_record_schemas_list == []


@pytest.mark.asyncio
async def test_filter():
    await create_user()
    await create_records(id=1)

    filtered_record_schemas_list = await records_s.filter(is_important=True)
    assert isinstance(filtered_record_schemas_list, list)
    for i in range(len(filtered_record_schemas_list)):
        assert isinstance(filtered_record_schemas_list[i], RecordOut)
        assert filtered_record_schemas_list[i].is_important
    assert len(filtered_record_schemas_list) == len(records) // 2 + 1


@pytest.mark.asyncio
async def test_get_obj_with_wrong_parameter():
    await create_user()
    await create_record(id=1)

    record_obj = await records_s.get_obj(id=2)
    assert record_obj is None


@pytest.mark.asyncio
async def test_get_obj():
    await create_user()
    await create_record(id=1)

    record_obj = await records_s.get_obj(id=1)
    assert isinstance(record_obj, Record)


@pytest.mark.asyncio
async def test_get_or_create_create():
    await create_user()

    record_obj, created = await records_s.get_or_create(defaults=record, creator_id=1)
    assert created
    assert isinstance(record_obj, Record)
    assert await Record.get_or_none(id=1)
    for key in record_in_data.keys():
        assert getattr(record_obj, key) == record_in_data[key]


@pytest.mark.asyncio
async def test_get_or_create_get():
    await create_user()
    await create_record(id=1)

    record_obj, created = await records_s.get_or_create(
        defaults=record, creator_id=1, name="name1"
    )
    assert not created
    assert isinstance(record_obj, Record)


@pytest.mark.asyncio
async def test_get_slice_without_kwargs():
    await create_user()
    await create_records(id=1)

    record_schemas_list = await records_s.get_slice(size=2)
    assert isinstance(record_schemas_list, list)
    assert len(record_schemas_list) == 2
    for i in range(len(records), len(records) - 2, -1):
        assert record_schemas_list[len(records) - i].id == i


@pytest.mark.asyncio
async def test_get_slice_with_kwargs():
    await create_user()
    await create_records(id=1)

    record_schemas_list = await records_s.get_slice(size=2, is_important=True)
    assert isinstance(record_schemas_list, list)
    assert len(record_schemas_list) == 2
    for i in range(len(records), len(records) - 2, -1):
        assert record_schemas_list[len(records) - i].is_important


@pytest.mark.asyncio
async def test_get_slice_with_filter():
    filter_obj = RecordFilter(
        is_important=True, date_from=None, date_to=None, order=None
    )
    await create_user()
    await create_records(id=1)

    record_schemas_list = await records_s.get_slice(filter_obj=filter_obj, size=2)
    assert isinstance(record_schemas_list, list)
    assert len(record_schemas_list) == 2
    for i in range(len(records), len(records) - 2, -1):
        assert record_schemas_list[len(records) - i].is_important


@pytest.mark.asyncio
async def test_get_slice_with_wrong_kwargs():
    await create_user()
    await create_records(id=1)

    record_schemas_list = await records_s.get_slice(size=2, creator_id=2)
    assert isinstance(record_schemas_list, list)
    assert len(record_schemas_list) == 0
