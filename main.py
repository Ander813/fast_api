from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from routers import records, websocket, users


app = FastAPI()


app.include_router(records.router,
                   prefix="/items",
                   tags=["records"])
app.include_router(websocket.router,
                   tags=["websocket"])

app.include_router(users.router,
                   prefix="/api-authentication",
                   tags=["users"])

register_tortoise(
    app=app,
    modules={'models': ['models.records', 'models.users']},
    db_url='sqlite://db.sqlite3',
    generate_schemas=True,
    add_exception_handlers=True
)
