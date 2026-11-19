"""Verify TLS and SMTP authentication without sending any email or printing secrets.

Run inside Vercel env run -e production to check hosted email configuration.
"""
import smtplib
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.core.config import get_settings
from app.services.mail import smtp_connection


def main():
    settings = get_settings()
    if not settings.email_ready:
        raise SystemExit('Email configuration is incomplete. Check SMTP_PASSWORD and the sender/TLS settings in Vercel Production.')
    try:
        with smtp_connection(settings):
            pass
    except smtplib.SMTPAuthenticationError:
        raise SystemExit('SMTP authentication failed. Check the Google App Password; do not use your normal Google password.')
    except (OSError, smtplib.SMTPException, ssl.SSLError):
        raise SystemExit('SMTP connection failed. Check the host, port, TLS and provider access settings.')
    print('SMTP TLS connection and authentication passed. No email was sent.')


if __name__ == '__main__':
    main()
