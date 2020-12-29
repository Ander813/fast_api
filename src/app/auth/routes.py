from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import Response
from tortoise.exceptions import IntegrityError

from .email import redis_pop_email
from .jwt import create_token, refresh_token_dependency
from .schemas import Token
from .social_auth.social_auth import oauth
from .social_auth import utils
from .tasks import (
    confirm_user_registration,
    reset_user_password,
    email_prefix,
    confirm_prefix,
    reset_prefix,
)
from src.app.base.schemas import Msg
from src.app.base.csrf import validate_csrf, ensure_csrf
from src.app.users.schemas import UserIn, UserInSocial
from src.app.users.services import users_s
from ..users.models import User


router = APIRouter()


@router.post(
    "/register",
    response_model=Msg,
    responses={400: {"Description": "bad request"}},
    dependencies=[Depends(ensure_csrf)],
)
async def user_registration(
    user: UserIn,
    task: BackgroundTasks,
):
    try:
        await users_s.create(user)
        await confirm_user_registration(user, task)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="User with such email address already exists"
        )
    return {"msg": "successfully registered"}


@router.get(
    "/register/confirm/{uuid}",
    response_model=Msg,
    responses={400: {"description": "Wrong or outdated uuid"}},
)
async def user_registration_confirm(uuid: str):
    email = await redis_pop_email(f"{email_prefix}:{confirm_prefix}:{uuid}")
    if not email:
        raise HTTPException(status_code=400, detail="Bad uuid")

    user = await users_s.get_obj(email=email)
    await user.activate()
    return {"msg": "email confirmed"}


@router.post(
    "/login/access-token", response_model=Token, dependencies=[Depends(ensure_csrf)]
)
async def user_token_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await users_s.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    response.set_cookie(
        "refresh_token",
        create_token(user.email, refresh=True)["refresh_token"],
        httponly=True,
    )
    return create_token(user.email)


@router.post(
    "/password-recovery",
    response_model=Msg,
    responses={404: {"description": "User not found"}},
    dependencies=[Depends(validate_csrf)],
)
async def user_recover_password(
    task: BackgroundTasks, email: str = Body(..., embed=True)
):
    user = users_s.get_obj(email=email)
    if user:
        await reset_user_password(email, task)
    else:
        raise HTTPException(status_code=404, detail="User with such email not found")

    return {"msg": "recovery email sent"}


@router.post(
    "/reset-password",
    response_model=Msg,
    responses={400: {"description": "Wrong or outdated uuid"}},
    dependencies=[Depends(validate_csrf)],
)
async def reset_password(uuid: str = Body(...), password: str = Body(...)):
    email = await redis_pop_email(f"{email_prefix}:{reset_prefix}:{uuid}")
    if not email:
        raise HTTPException(status_code=400, detail="Bad uuid")

    user = await users_s.get_obj(email=email)
    await users_s.set_password(user=user, password=password)
    return {"msg": "password reset successfully"}


@router.post(
    "/refresh",
    response_model=Token,
    dependencies=[Depends(validate_csrf), Depends(ensure_csrf)],
)
async def user_token_refresh(user: User = Depends(refresh_token_dependency)):
    return create_token(user.email)


@router.get("/login/vk")
async def vk_login(request: Request):
    redirect_uri = request.url_for("vk_auth")
    return await oauth.vk.authorize_redirect(request, redirect_uri)


@router.get("/vk", dependencies=[Depends(ensure_csrf)])
async def vk_auth(request: Request, response: Response):
    token = await oauth.vk.authorize_access_token(request, method="GET")
    user, _ = await users_s.get_or_create_social(
        email=token["email"], defaults=UserInSocial(email=token["email"])
    )
    response.set_cookie(
        "refresh_token",
        create_token(user.email, refresh=True)["refresh_token"],
        httponly=True,
    )
    return create_token(user.email)


@router.get("/login/git")
async def git_login(request: Request):
    redirect_uri = request.url_for("git_auth")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/git", dependencies=[Depends(ensure_csrf)])
async def git_auth(request: Request, response: Response):
    token = await oauth.github.authorize_access_token(request)
    request.session["token"] = token
    emails = (
        await oauth.github.get("https://api.github.com/user/emails", request=request)
    ).json()
    email = utils.get_git_primary_email(emails)
    user, _ = await users_s.get_or_create_social(
        email=email, defaults=UserInSocial(email=email)
    )
    response.set_cookie(
        "refresh_token",
        create_token(user.email, refresh=True)["refresh_token"],
        httponly=True,
    )
    return create_token(user.email)
