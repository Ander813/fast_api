from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import Response
from tortoise.exceptions import IntegrityError

from .jwt import create_token, create_refresh_token
from .permissions import get_current_user
from .schemas import Token
from .social_auth.social_auth import oauth
from .social_auth import utils
from .tasks import confirm_user_registration, email_prefix
from src.app.base.schemas import Msg
from src.app.users.schemas import UserIn, UserInSocial
from src.app.users.services import users_s
from ..base.redis import Redis
from ..users.models import User
from ...conf import settings

router = APIRouter()


@router.post('/register',
             response_model=Msg,
             responses={400: {'Description': 'bad request'}})
async def user_registration(user: UserIn, task: BackgroundTasks):
    try:
        await users_s.create(user)
        await confirm_user_registration(user, task)
    except IntegrityError:
        raise HTTPException(status_code=400,
                            detail='User with such email address already exists')
    return {'msg': 'successfully registered'}


@router.get('/register/confirm/{uuid}', response_model=Msg)
async def user_registration_confirm(uuid: str):
    redis_instance = await Redis(host=settings.REDIS_HOST,
                                 password=settings.REDIS_PASSWORD,
                                 db=settings.REDIS_DB).get_instance()
    email = await redis_instance.get(f'{email_prefix}:{uuid}', encoding='utf-8')
    await redis_instance.delete(f'{email_prefix}:{uuid}')
    if email:
        user = await users_s.get_obj(email=email)
        await user.activate()
        return {'msg': 'email confirmed'}
    else:
        return {'msg': 'something went wrong with email confirmation'}


@router.post('/login/access-token',
             response_model=Token)
async def user_token_login(response: Response,
                           form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_s.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    response.set_cookie('refresh_token', create_refresh_token())
    return create_token(user.email)


@router.get('/refresh',
            response_model=Token)
async def user_token_refresh(request: Request,
                             response: Response,
                             user: User = Depends(get_current_user)):
    refresh_token = request.cookies.get('refresh_token', None)
    if refresh_token:
        response.set_cookie('refresh_token', create_refresh_token())
    else:
        return HTTPException(status_code=401, detail='Unauthorized')
    return create_token(user.email)


@router.get('/login/vk')
async def vk_login(request: Request):
    redirect_uri = request.url_for('vk_auth')
    return await oauth.vk.authorize_redirect(request, redirect_uri)


@router.get('/vk')
async def vk_auth(request: Request):
    token = await oauth.vk.authorize_access_token(request, method='GET')
    user, _ = await users_s.get_or_create_social(email=token['email'],
                                                 defaults=UserInSocial(email=token['email']))
    return create_token(user.email, token)


@router.get('/login/git')
async def git_login(request: Request):
    redirect_uri = request.url_for('git_auth')
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get('/git')
async def git_auth(request: Request):
    token = await oauth.github.authorize_access_token(request)
    request.session['token'] = token
    emails = (await oauth.github.get('https://api.github.com/user/emails',
                                     request=request)).json()
    email = utils.get_git_primary_email(emails)
    user, _ = await users_s.get_or_create_social(email=email,
                                                 defaults=UserInSocial(email=email))
    return create_token(user.email, token)
