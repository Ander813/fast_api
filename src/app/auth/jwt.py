from datetime import timedelta, datetime
from jose import jwt
from src.conf import settings


ALGORITHM = "HS256"
access_token_subject = "access"
refresh_token_subject = "refresh"


def create_token(email: str, refresh: bool = False):
    data = {"email": email}
    if refresh:
        access_token_expire = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        return {
            "refresh_token": create_refresh_token(
                data=data, expire_delta=access_token_expire
            )
        }
    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data=data, expire_delta=access_token_expire
        ),
        "token_type": "bearer",
    }


def create_access_token(*, data: dict, expire_delta: timedelta = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now() + expire_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": access_token_subject})
    return jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)


def create_refresh_token(*, data: dict, expire_delta: timedelta = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now() + expire_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"sub": refresh_token_subject, "exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)
