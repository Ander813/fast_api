from datetime import timedelta, datetime

from fastapi import HTTPException, Depends
from jose import jwt, JWTError
from starlette.requests import Request
from starlette.responses import Response

from src.app.auth.permissions import get_current_user
from src.app.auth.schemas import TokenPayload
from src.conf import settings


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
    return jwt.encode(to_encode, settings.SECRET_KEY, settings.JWT_ALGORITHM)


def create_refresh_token(*, data: dict, expire_delta: timedelta = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now() + expire_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"sub": refresh_token_subject, "exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, settings.JWT_ALGORITHM)


def refresh_token_dependency(
    request: Request, response: Response, user=Depends(get_current_user)
):
    token = request.cookies.get("refresh_token", None)

    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    if user.email != token_data.email:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    response.set_cookie(
        "refresh_token",
        create_token(email=user.email, refresh=True)["refresh_token"],
        httponly=True,
    )
    return user
