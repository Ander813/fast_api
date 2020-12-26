from pathlib import Path

from src.app.base.email import send_email
from src.conf import settings
from ..base.redis import Redis


confirm_email_endpoint = f'{settings.SERVER_HOST}/api/v1/auth/register/confirm'


def send_registration_email(email_to: str, uuid: str) -> None:
    subject_template = f'{settings.PROJECT_NAME} - User registration'
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / 'email-registration.html') as file:
        html_template = file.read()
    link = f'{confirm_email_endpoint}/{uuid}'

    send_email(email_to=email_to,
               subject_template=subject_template,
               html_template=html_template,
               context={'server_host': settings.SERVER_HOST,
                        'link': link})


def send_reset_password_email(email_to: str, uuid: str) -> None:
    subject_template = f'{settings.PROJECT_NAME} - Password reset'
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / 'password-reset.html') as file:
        html_template = file.read()

    send_email(email_to=email_to,
               subject_template=subject_template,
               html_template=html_template,
               context={'server_host': settings.SERVER_HOST,
                        'uuid': uuid})


async def redis_pop_email(key: str):
    redis_instance = await Redis(host=settings.REDIS_HOST,
                                 password=settings.REDIS_PASSWORD,
                                 db=settings.REDIS_DB).get_instance()
    email = await redis_instance.get(key, encoding='utf-8')
    await redis_instance.delete(key)
    return email
