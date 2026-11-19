import ssl
from unittest.mock import MagicMock
import pytest
from app.core.config import Settings
from app.services import mail


def gmail_settings(**overrides):
    values = dict(environment='production', smtp_host='smtp.gmail.com', smtp_port=587,
                  smtp_starttls=True, smtp_username='sender@gmail.com',
                  smtp_password='abcd efgh ijkl mnop', mail_from='CodeArena <sender@gmail.com>',
                  frontend_url='https://codearena.example.com')
    values.update(overrides)
    return Settings(_env_file=None, secret_key='test-only-signing-key-at-least-32-characters',
                    postgres_password='test-only-database', **values)


def test_gmail_connects_with_verified_tls_before_authentication(monkeypatch):
    config = gmail_settings()
    client = MagicMock()
    constructor = MagicMock()
    constructor.return_value.__enter__.return_value = client
    monkeypatch.setattr(mail.smtplib, 'SMTP', constructor)
    monkeypatch.setattr(mail, 'get_settings', lambda: config)
    mail.send_action('recipient@example.com', 'test-once-token', 'verify')
    constructor.assert_called_once_with('smtp.gmail.com', 587, timeout=10)
    methods = [call[0] for call in client.method_calls]
    assert methods == ['ehlo', 'starttls', 'ehlo', 'login', 'send_message']
    context = client.starttls.call_args.kwargs['context']
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    client.login.assert_called_once_with('sender@gmail.com', 'abcdefghijklmnop')
    message = client.send_message.call_args.args[0]
    assert message['From'] == 'CodeArena <sender@gmail.com>'
    assert message['To'] == 'recipient@example.com'
    assert 'https://codearena.example.com/verify-email?token=test-once-token' in message.get_content()
    assert 'abcdefghijklmnop' not in message.get_content()


@pytest.mark.parametrize('overrides', [
    {'smtp_password': ''},
    {'smtp_starttls': False},
    {'smtp_port': 465},
    {'mail_from': 'CodeArena <different@gmail.com>'},
])
def test_incomplete_or_insecure_gmail_configuration_cannot_send(monkeypatch, overrides):
    config = gmail_settings(**overrides)
    constructor = MagicMock()
    monkeypatch.setattr(mail.smtplib, 'SMTP', constructor)
    assert config.email_ready is False
    with pytest.raises(OSError, match='not fully configured'):
        with mail.smtp_connection(config):
            pass
    constructor.assert_not_called()


def test_google_credentials_never_fall_back_to_another_provider_key():
    config = gmail_settings(smtp_password='', resend_api_key='resend-test-only-key')
    assert config.smtp_login_password == ''
    assert config.email_ready is False


def test_reset_email_contains_reset_link(monkeypatch):
    config = gmail_settings()
    client = MagicMock()
    constructor = MagicMock()
    constructor.return_value.__enter__.return_value = client
    monkeypatch.setattr(mail.smtplib, 'SMTP', constructor)
    monkeypatch.setattr(mail, 'get_settings', lambda: config)
    mail.send_action('recipient@example.com', 'test-reset-token', 'reset')
    message = client.send_message.call_args.args[0]
    assert 'reset-password?token=test-reset-token' in message.get_content()
    assert message['Subject'] == 'Reset your CodeArena password'


def test_local_mailpit_remains_usable_without_smtp_authentication(monkeypatch):
    config = gmail_settings(environment='development', smtp_host='127.0.0.1', smtp_port=1025,
                            smtp_starttls=False, smtp_username='', smtp_password='')
    client = MagicMock()
    constructor = MagicMock()
    constructor.return_value.__enter__.return_value = client
    monkeypatch.setattr(mail.smtplib, 'SMTP', constructor)
    with mail.smtp_connection(config):
        pass
    client.starttls.assert_not_called()
    client.login.assert_not_called()
