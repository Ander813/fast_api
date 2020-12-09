from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from src.conf import settings
from src.app.router import main_router

app = FastAPI()


app.include_router(main_router,
                   prefix="/v1")

register_tortoise(
    app=app,
    modules={'models': settings.APPS_MODELS},
    db_url='sqlite://db.sqlite3',
    generate_schemas=True,
    add_exception_handlers=True
)
