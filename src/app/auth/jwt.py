from datetime import timedelta, datetime
from jose import jwt
from src.conf import settings


ALGORITHM = "HS256"
access_token_subject = 'access'


def create_token(email: str):
    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        'access_token': create_access_token(
            data={'email': email},
            expire_delta=access_token_expire
        ),
        'token_type': 'bearer',
    }


def create_access_token(*, data: dict, expire_delta: timedelta = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now() + expire_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({'exp': expire, 'sub': access_token_subject})
    return jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)
