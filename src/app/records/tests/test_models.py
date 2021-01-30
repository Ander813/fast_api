import pytest
from tortoise.contrib.test import initializer, finalizer

from src.app.records.models import Record
from src.app.users.schemas import UserIn
from src.app.users.services import users_s
from src.conf import settings


test_record = {
    "name": "test_name",
    "text": "test_text",
    "is_important": "is_important",
    "creator_id": 1,
}
user_email = "test@mail.ru"
user_password = "Test1234"
user = UserIn(email=user_email, password=user_password)


@pytest.fixture(autouse=True)
def initialize_tests(request):
    initializer(settings.APPS_MODELS)
    request.addfinalizer(finalizer)


async def create_user():
    return await users_s.create(user)


@pytest.mark.asyncio
async def test_create_record():
    await create_user()

    await Record.create(**test_record)
    assert await Record.get_or_none(id=1)
