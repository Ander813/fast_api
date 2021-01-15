from jose import jwt

from src.app.auth.jwt import create_token
from src.conf import settings

test_email = "test_email@mail.ru"


def test_create_access_token():
    token = create_token(test_email)
    assert isinstance(token, dict)
    assert token["access_token"]
    assert token["token_type"] == "bearer"

    payload = jwt.decode(
        token["access_token"], settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["email"] == test_email
    assert payload["sub"] == "access"


def test_create_refresh_token():
    token = create_token(test_email, refresh=True)
    assert isinstance(token, dict)
    assert token["refresh_token"]

    payload = jwt.decode(
        token["refresh_token"], settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["email"] == test_email
    assert payload["sub"] == "refresh"
