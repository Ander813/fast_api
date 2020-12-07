from tortoise import Tortoise, run_async

from models import records


async def init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['models.records']}
    )
    await Tortoise.generate_schemas()

run_async(init())
