from src.conf import settings
import emails
from emails.template import JinjaTemplate


def send_email(email_to: str, subject_template='', html_template='', context: dict = {}):
    assert settings.EMAILS_ENABLED, 'please configure email backend to send emails'

    message = emails.Message(subject=JinjaTemplate(subject_template),
                             html=JinjaTemplate(html_template),
                             mail_from=(settings.EMAIL_FROM_NAME, settings.EMAIL_FROM_EMAIL))
    smtp_options = {'host': settings.SMTP_HOST,
                    'port': settings.SMTP_PORT,
                    'user': settings.EMAIL_HOST_USER,
                    'password': settings.EMAIL_HOST_PASSWORD}
    if settings.SMTP_TLS:
        smtp_options['tls'] = True

    message.send(email_to, render=context, smtp=smtp_options)
