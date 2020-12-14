from . import settings


TORTOISE_ORM = {
    "connections": {"default": settings.DB_URI},
    "apps": {
        "models": {
            "models": settings.APPS_MODELS,
            "default_connection": "default",
        },
    },
}
