import smtplib
import ssl
from contextlib import contextmanager
from email.message import EmailMessage
from app.core.config import get_settings


@contextmanager
def smtp_connection(settings):
    if not settings.email_ready:
        raise OSError('Email service is not fully configured.')
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        smtp.ehlo()
        if settings.smtp_starttls:
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_login_password)
        yield smtp


def send_action(email: str, token: str, purpose: str):
    settings = get_settings()
    path = 'verify-email' if purpose == 'verify' else 'reset-password'
    message = EmailMessage()
    message['From'] = settings.mail_from
    message['To'] = email
    message['Subject'] = 'Verify your CodeArena account' if purpose == 'verify' else 'Reset your CodeArena password'
    message.set_content(f'Continue securely using this link:\n\n{settings.frontend_url}/{path}?token={token}\n\nThis link expires in 30 minutes and works once. If you did not request it, ignore this message.')
    with smtp_connection(settings) as smtp:
        smtp.send_message(message)
