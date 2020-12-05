from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from routers import items


app = FastAPI()


app.include_router(items.router,
                   prefix="/items",
                   tags=["items"])

register_tortoise(
    app=app,
    modules={'models': ['models.record']},
    db_url='sqlite://db.sqlite3',
    add_exception_handlers=True
)
