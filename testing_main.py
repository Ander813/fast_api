from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from src.conf import settings
from src.app.router import main_router
from src.app.admin_router import admin_router
from src.conf.middleware import middleware
from src.conf.exceptions import exceptions


app = FastAPI(middleware=middleware, exception_handlers=exceptions)

app.include_router(main_router, prefix="/api/v1")

app.include_router(admin_router, prefix="/admin")
