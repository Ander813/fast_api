import aioredis
import asyncio


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        instance_key = f'{kwargs["host"]}{kwargs.get("password", None)}{kwargs.get("db", None)}'
        if instance_key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[instance_key] = instance
        return cls._instances[instance_key]


class Redis(metaclass=SingletonMeta):
    def __init__(self, *, host: str, password: str = None, db: int = None):
        self.host = host
        self.password = password
        self.db = db
        self.instance = None

    async def get_instance(self):
        if not self.instance:
            self.instance = await aioredis.create_redis_pool(self.host,
                                                             password=self.password,
                                                             db=self.db)
        return self.instance
