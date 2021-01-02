from starlette.testclient import TestClient

from src.app.auth.jwt import create_token
from src.app.records.schemas import RecordIn
from src.app.records.services import records_s
from src.app.users.schemas import UserIn
from src.app.users.services import users_s
from testing_main import app
import json
import asyncio

user_email = "test@mail.ru"
user_password = "12345"
user = UserIn(email=user_email, password=user_password)
token = create_token(user_email)
authorization = {"Authorization": f"Bearer {token['access_token']}"}
records = [
    RecordIn(name=f"{i}", text=f"text {i}", is_important=False if i % 2 == 1 else True)
    for i in range(5)
]

client = TestClient(app)


def create_user():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(loop.create_task(users_s.create(user)))


def create_records(id: int):
    loop = asyncio.get_event_loop()
    tasks = [records_s.create(records[i]) for i in range(len(records))]
    return loop.run_until_complete(asyncio.gather(*tasks))


def test_post_record_unauthorized():
    response = client.post(app.url_path_for("create_record"), data=records[0].json())
    assert response.status_code == 401


def test_post_record_authorized():
    with client:
        create_user()
        response = client.post(
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


def test_get_records_unauthorized():
    response = client.get(app.url_path_for("get_records"))
    assert response.status_code == 401
