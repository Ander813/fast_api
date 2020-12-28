from fastapi.responses import ORJSONResponse
from fastapi_csrf_protect.exceptions import CsrfProtectError
from starlette.requests import Request


def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})


exceptions = {CsrfProtectError: csrf_protect_exception_handler}
