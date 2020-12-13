from fastapi import FastAPI
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.fastapi import register_tortoise
from src.conf import settings
from src.app.router import main_router


middleware = [
    Middleware(CORSMiddleware,
               allow_origins=["*"],
               allow_credentials=True,
               allow_methods=["*"],
               allow_headers=["*"]),
    Middleware(SessionMiddleware,
               secret_key=settings.SECRET_KEY,
               same_site='None')
]

app = FastAPI(middleware=middleware)

app.include_router(main_router,
                   prefix="/api/v1")

register_tortoise(
    app=app,
    modules={'models': settings.APPS_MODELS},
    db_url='sqlite://db.sqlite3',
    generate_schemas=True,
    add_exception_handlers=True
)
