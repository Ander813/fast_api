from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import IntegrityError

from src.app.auth.jwt import create_token
from src.app.auth.schemas import Token
from src.app.base.schemas import Msg
from src.app.users.schemas import UserIn
from src.app.users.services import users_s

router = APIRouter()


@router.post('/register',
             response_model=Msg,
             responses={400: {'Description': 'bad request'}})
async def user_registration(user: UserIn):
    try:
        user = await users_s.create_user(user)
    except IntegrityError:
        raise HTTPException(status_code=400,
                            detail='User with such email address already exists')
    return {'msg': 'successfully registered'}


@router.post('/login/access-token',
             response_model=Token)
async def user_token_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_s.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    return create_token(user.email)