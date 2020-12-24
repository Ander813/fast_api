from pathlib import Path

from src.app.base.email import send_email
from src.conf import settings


confirm_email_endpoint = 'api/v1/auth/register/confirm'


def send_registration_email(email_to: str, uuid: str) -> None:
    subject_template = f'{settings.PROJECT_NAME} - User registration'
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / 'email-registration.html') as file:
        html_template = file.read()
    link = f'{settings.SERVER_HOST}/{confirm_email_endpoint}/{uuid}'

    send_email(email_to=email_to,
               subject_template=subject_template,
               html_template=html_template,
               context={'server_host': settings.SERVER_HOST,
                        'link': link})