"""Repeatable local HTTP -> Next.js proxy -> API -> PostgreSQL/Redis/SMTP check.

Creates a uniquely named QA account. Requires both app servers and Mailpit.
Never prints passwords, cookies or email tokens.
"""
import re
import secrets
import uuid
import httpx

BASE = 'http://127.0.0.1:3000'
MAIL = 'http://127.0.0.1:8025'
email = f'qa-{uuid.uuid4().hex}@example.com'
password = 'Qa-' + secrets.token_urlsafe(24) + '-2026'


def expect(response, status):
    assert response.status_code == status, f'{response.request.url.path}: expected {status}, got {response.status_code}: {response.text}'
    return response


def email_token(subject):
    messages = httpx.get(MAIL + '/api/v1/messages', timeout=10).json()['messages']
    match = next(m for m in messages if m['Subject'] == subject and any(t['Address'] == email for t in m['To']))
    detail = httpx.get(MAIL + '/api/v1/message/' + match['ID'], timeout=10).json()
    return re.search(r'token=([\w-]+)', detail['Text']).group(1)


with httpx.Client(base_url=BASE, headers={'Origin': BASE}, timeout=15) as client:
    expect(client.get('/'), 200)
    expect(client.get('/api/v1/health'), 200)
    expect(client.post('/api/v1/auth/register', json={'email': email, 'password': password, 'full_name': 'Local QA Developer', 'country': 'India', 'user_type': 'developer'}), 201)
    token = email_token('Verify your CodeArena account')
    expect(client.post('/api/v1/auth/verify-email', json={'token': token}), 200)
    expect(client.post('/api/v1/auth/login', json={'email': email, 'password': password}), 200)
    expect(client.patch('/api/v1/users/me/profile', json={'full_name': 'Local QA Developer', 'country': 'India', 'institution': 'QA', 'bio': 'Full-stack smoke test.'}), 200)
    assert expect(client.get('/api/v1/users/me'), 200).json()['onboarded'] is True
    expect(client.get('/api/v1/admin/access'), 403)
    expect(client.post('/api/v1/auth/refresh'), 200)
    assert len(expect(client.get('/api/v1/auth/sessions'), 200).json()) == 1
    expect(client.post('/api/v1/auth/forgot-password', json={'email': email}), 200)
    reset = email_token('Reset your CodeArena password')
    new_password = 'Reset-' + secrets.token_urlsafe(24) + '-2026'
    expect(client.post('/api/v1/auth/reset-password', json={'token': reset, 'password': new_password}), 200)
    expect(client.get('/api/v1/users/me'), 401)
    expect(client.post('/api/v1/auth/login', json={'email': email, 'password': new_password}), 200)
    expect(client.post('/api/v1/auth/logout'), 200)
    expect(client.get('/api/v1/users/me'), 401)
print('PASS: registration, SMTP verification, login, profile persistence, RBAC, renewal, recovery, revocation, logout.')
print('A uniquely named QA account and its audit records remain in the local database.')
