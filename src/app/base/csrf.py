from fastapi import Depends
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response

from src.conf import settings


class CsrfSettings(BaseModel):
    secret_key: str = settings.SECRET_KEY


class Csrf(CsrfProtect):
    _httponly = False


@Csrf.load_config
def get_config():
    return CsrfSettings()


def validate_csrf(request: Request, csrf: Csrf = Depends()):
    if settings.DEBUG:
        auth = request.cookies.get("csrftoken", None)
    else:
        auth = request.headers.get("X-CSRFToken", None)
    if not auth:
        raise CsrfProtectError
    csrf_token = csrf.get_csrf_from_headers(auth)
    csrf.validate_csrf(csrf_token)


def ensure_csrf(response: Response, csrf: Csrf = Depends()):
    csrf_token = csrf.generate_csrf()
    response.set_cookie("csrftoken", csrf_token)
