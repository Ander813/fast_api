from fastapi import Security, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from .jwt import ALGORITHM
from .schemas import TokenPayload
from ..users.services import users_s
from ...conf import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/login/access-token'
)


async def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    user = await users_s.get_obj(email=token_data.email)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user
