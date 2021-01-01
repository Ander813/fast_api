from fastapi import Security, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .schemas import TokenPayload
from ..users.models import User
from ..users.services import users_s
from ...conf import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/access-token", scheme_name="token_auth"
)


async def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
<<<<<<< HEAD
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    user = await users_s.get_obj(email=token_data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def user_for_refresh(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
=======
>>>>>>> 9e87bbc... Refresh token endpoint now validates refresh token
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    user = await users_s.get_obj(email=token_data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_superuser(user: User = Depends(get_current_user)):
    if user.is_superuser:
        return user
    else:
        raise HTTPException(status_code=403, detail="You don't have enough permissions")
