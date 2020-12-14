from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from tortoise.exceptions import IntegrityError

from .jwt import create_token
from .schemas import Token
from .social_auth.social_auth import oauth
from .social_auth import utils
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


@router.get('/login/vk')
async def vk_login(request: Request):
    redirect_uri = request.url_for('vk_auth')
    return await oauth.vk.authorize_redirect(request, redirect_uri)


@router.get('/vk')
async def vk_auth(request: Request):
    token = await oauth.vk.authorize_access_token(request, method='GET')
    user = await oauth.vk.parse_id_token(request, token)


@router.get('/login/git')
async def git_login(request: Request):
    redirect_uri = request.url_for('git_auth')
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get('/git')
async def git_auth(request: Request):
    token = await oauth.github.authorize_access_token(request)
    emails = (await oauth.github.get('https://api.github.com/user/emails', request=request)).json()
    email = utils.get_git_primary_email(emails)
    return create_token(email, token['access_token'])
