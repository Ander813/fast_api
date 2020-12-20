from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from src.conf import settings
from src.app.router import main_router
from src.app.admin_router import admin_router
from src.conf.middleware import middleware


app = FastAPI(middleware=middleware)

app.include_router(main_router,
                   prefix="/api/v1")

app.include_router(admin_router,
                   prefix="/admin")

register_tortoise(
    app=app,
    modules={'models': settings.APPS_MODELS},
    db_url=settings.DB_URI,
    generate_schemas=True,
    add_exception_handlers=True
)
