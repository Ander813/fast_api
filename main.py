from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from routers import items, websocket


app = FastAPI()


app.include_router(items.router,
                   prefix="/items",
                   tags=["items"])
app.include_router(websocket.router,
                   tags=["websocket"])

"""register_tortoise(
    app=app,
    modules={'models': ['models.records']},
    db_url='sqlite://db.sqlite3',
    add_exception_handlers=True
)"""
