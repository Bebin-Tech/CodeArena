import pytest
from app.core.config import Settings


def settings(**values):
    return Settings(_env_file=None, secret_key='test-only-signing-key-at-least-32-characters', **values)


@pytest.mark.parametrize('prefix', ['postgres://', 'postgresql://'])
def test_neon_url_uses_psycopg3(prefix):
    config = settings(database_url=prefix + 'user:password@db.example/db?sslmode=require')
    assert config.db_url == 'postgresql+psycopg://user:password@db.example/db?sslmode=require'


def test_marketplace_environment_aliases(monkeypatch):
    monkeypatch.setenv('KV_URL', 'rediss://redis.example:6379')
    monkeypatch.setenv('RESEND_API_KEY', 'test-only-provider-key')
    monkeypatch.delenv('REDIS_URL', raising=False)
    monkeypatch.delenv('SMTP_PASSWORD', raising=False)
    config = settings(postgres_password='local-only-test', smtp_host='smtp.resend.com')
    assert config.redis_url == 'rediss://redis.example:6379'
    assert config.smtp_login_password == 'test-only-provider-key'


def test_production_domain_defaults_and_secure_cookies(monkeypatch):
    monkeypatch.setenv('VERCEL', '1')
    monkeypatch.setenv('VERCEL_PROJECT_PRODUCTION_URL', 'codearena.example.com')
    monkeypatch.delenv('FRONTEND_URL', raising=False)
    monkeypatch.delenv('API_URL', raising=False)
    config = settings(postgres_password='local-only-test', environment='production')
    assert config.frontend_url == 'https://codearena.example.com'
    assert config.api_url == config.frontend_url
    assert config.secure_cookies


def test_unconfigured_database_is_rejected(monkeypatch):
    monkeypatch.delenv('POSTGRES_PASSWORD', raising=False)
    monkeypatch.delenv('DATABASE_URL', raising=False)
    with pytest.raises(ValueError, match='Configure DATABASE_URL'):
        settings()


def test_forwarded_ip_is_only_used_inside_vercel(context, monkeypatch):
    from starlette.requests import Request
    from app.core.security import throttle
    _, _, _, counters = context
    request = Request({'type': 'http', 'headers': [(b'x-vercel-forwarded-for', b'203.0.113.8')], 'client': ('127.0.0.1', 1234)})
    monkeypatch.delenv('VERCEL', raising=False)
    throttle(request, 'test')
    assert 'rate:test:127.0.0.1' in counters.values
    monkeypatch.setenv('VERCEL', '1')
    throttle(request, 'test')
    assert 'rate:test:203.0.113.8' in counters.values


def test_production_reports_unconfigured_email(monkeypatch):
    from app.api import oauth
    config = settings(postgres_password='local-only-test', environment='production')
    monkeypatch.setattr(oauth, 'settings', config)
    assert oauth.providers()['email'] is False
    config.smtp_host = 'smtp.resend.com'
    config.smtp_starttls = True
    config.smtp_username = 'resend'
    config.smtp_password = 'test-only-key'
    config.mail_from = 'CodeArena <accounts@example.com>'
    assert oauth.providers()['email'] is True
