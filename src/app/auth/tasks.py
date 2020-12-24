import uuid as _
from src.conf import settings
from fastapi import BackgroundTasks
from src.app.users.schemas import UserIn
from src.app.base.redis import Redis
from .email import send_registration_email


email_prefix = 'email'


async def confirm_user_registration(user: UserIn, task: BackgroundTasks):
    redis_instance = await Redis(host=settings.REDIS_HOST,
                                 password=settings.REDIS_PASSWORD,
                                 db=settings.REDIS_DB).get_instance()
    uuid = str(_.uuid4())
    await redis_instance.set(f'{email_prefix}:{uuid}', user.email, expire=settings.EMAIL_CONFIRM_EXPIRE)
    task.add_task(send_registration_email, user.email, uuid)