import uuid
from datetime import timedelta
import jwt
from sqlalchemy import select
from app.core.config import get_settings
from app.core.security import COOKIE, password_hasher, token_digest, utcnow
from app.models import ActionToken, AuditLog, User, UserSession

PASSWORD = 'Testing-codearena-123'


def signup(client, mail, email='developer@example.com', verify=True):
    result = client.post('/api/v1/auth/register', json={'email': email, 'password': PASSWORD, 'full_name': 'Arena Developer', 'country': 'India', 'user_type': 'developer'})
    assert result.status_code == 201, result.text
    if verify:
        result = client.post('/api/v1/auth/verify-email', json={'token': mail[-1][1]})
        assert result.status_code == 200, result.text
    return email


def login(client, email='developer@example.com', password=PASSWORD):
    return client.post('/api/v1/auth/login', json={'email': email, 'password': password})


def test_full_account_lifecycle(context):
    client, db, mail, _ = context
    signup(client, mail)
    user = db.scalar(select(User))
    assert user.password_hash.startswith('$argon2id$')
    assert password_hasher.verify(PASSWORD, user.password_hash)
    assert db.scalar(select(ActionToken)).digest == token_digest(mail[0][1])
    result = login(client)
    assert result.status_code == 200
    assert 'httponly' in result.headers['set-cookie'].lower()
    assert 'samesite=lax' in result.headers['set-cookie'].lower()
    assert 'password' not in result.text
    assert client.get('/api/v1/users/me').json()['email'] == user.email
    profile = {'full_name': 'Updated Developer', 'country': 'India', 'institution': 'Code Club', 'bio': 'Learning algorithms'}
    result = client.patch('/api/v1/users/me/profile', json=profile)
    assert result.json()['onboarded'] is True
    db.expire_all()
    assert db.get(User, user.id).bio == profile['bio']
    assert client.get('/api/v1/auth/sessions').json()[0]['current']
    assert client.post('/api/v1/auth/logout').status_code == 200
    assert client.get('/api/v1/users/me').status_code == 401
    assert db.scalars(select(AuditLog)).all()


def test_verification_required_and_no_replay(context):
    client, db, mail, _ = context
    signup(client, mail, verify=False)
    assert login(client).status_code == 403
    token = mail[-1][1]
    assert client.post('/api/v1/auth/verify-email', json={'token': token}).status_code == 200
    assert client.post('/api/v1/auth/verify-email', json={'token': token}).status_code == 400


def test_expired_action_tokens(context):
    client, db, mail, _ = context
    signup(client, mail, verify=False)
    token = db.scalar(select(ActionToken))
    token.expires_at = utcnow() - timedelta(seconds=1)
    db.commit()
    assert client.post('/api/v1/auth/verify-email', json={'token': mail[-1][1]}).status_code == 400


def test_recovery_revokes_sessions_and_token(context):
    client, db, mail, _ = context
    signup(client, mail)
    assert login(client).status_code == 200
    known = client.post('/api/v1/auth/forgot-password', json={'email': 'developer@example.com'})
    unknown = client.post('/api/v1/auth/forgot-password', json={'email': 'nobody@example.com'})
    assert known.json() == unknown.json()
    token = mail[-1][1]
    new_password = 'A-new-strong-password-456'
    assert client.post('/api/v1/auth/reset-password', json={'token': token, 'password': new_password}).status_code == 200
    assert client.get('/api/v1/users/me').status_code == 401
    assert login(client).status_code == 401
    assert login(client, password=new_password).status_code == 200
    assert client.post('/api/v1/auth/reset-password', json={'token': token, 'password': PASSWORD}).status_code == 400


def test_public_role_escalation_and_profile_injection_rejected(context):
    client, db, mail, _ = context
    assert client.post('/api/v1/auth/register', json={'email': 'admin@example.com', 'password': PASSWORD, 'full_name': 'Bad Admin', 'country': 'India', 'user_type': 'super_admin'}).status_code == 422
    signup(client, mail)
    login(client)
    assert client.get('/api/v1/admin/access').status_code == 403
    assert client.patch('/api/v1/users/me/profile', json={'full_name': 'Developer', 'country': 'India', 'role': 'super_admin'}).status_code == 422
    user = db.scalar(select(User))
    user.role = 'platform_admin'
    db.commit()
    assert client.get('/api/v1/admin/access').status_code == 200


def test_csrf_and_password_validation(context):
    client, _, _, _ = context
    assert client.post('/api/v1/auth/login', headers={'Origin': 'https://evil.example'}, json={'email': 'x@example.com', 'password': 'x'}).status_code == 403
    assert client.post('/api/v1/auth/register', json={'email': 'x@example.com', 'password': 'short', 'full_name': 'Bad', 'country': 'India'}).status_code == 422
    assert client.get('/api/v1/users/me').status_code == 401


def test_session_rotation_revocation_and_ownership(context):
    client, db, mail, _ = context
    signup(client, mail)
    login(client)
    old_cookie = client.cookies.get(COOKIE)
    assert client.post('/api/v1/auth/refresh').status_code == 200
    new_cookie = client.cookies.get(COOKIE)
    assert old_cookie != new_cookie
    client.cookies.set(COOKIE, old_cookie, domain='testserver.local', path='/')
    assert client.get('/api/v1/users/me').status_code == 401
    client.cookies.set(COOKIE, new_cookie, domain='testserver.local', path='/')
    assert client.delete(f'/api/v1/auth/sessions/{uuid.uuid4()}').status_code == 404
    other = User(email='other@example.com', full_name='Other', country='India', role='developer', verified=True)
    db.add(other); db.flush()
    other_session = UserSession(user_id=other.id, expires_at=utcnow() + timedelta(minutes=10))
    db.add(other_session); db.commit()
    assert client.delete(f'/api/v1/auth/sessions/{other_session.id}').status_code == 404
    current = client.get('/api/v1/auth/sessions').json()[0]
    assert client.delete('/api/v1/auth/sessions/' + current['id']).status_code == 200
    assert client.get('/api/v1/users/me').status_code == 401


def test_suspension_and_jwt_expiry(context):
    client, db, mail, _ = context
    signup(client, mail); login(client)
    token = client.cookies.get(COOKIE)
    settings = get_settings()
    claims = jwt.decode(token, settings.secret_key, algorithms=['HS256'], audience='codearena-web', issuer='codearena')
    claims['exp'] = utcnow() - timedelta(seconds=1)
    expired = jwt.encode(claims, settings.secret_key, algorithm='HS256')
    client.cookies.set(COOKIE, expired, domain='testserver.local', path='/')
    assert client.get('/api/v1/users/me').status_code == 401
    client.cookies.set(COOKIE, token, domain='testserver.local', path='/')
    user = db.scalar(select(User)); user.suspended = True; db.commit()
    assert client.get('/api/v1/users/me').status_code == 401
    assert login(client).status_code == 401


def test_rate_limit_and_duplicate_registration(context):
    client, db, mail, _ = context
    signup(client, mail)
    before = len(mail)
    signup(client, mail, verify=False)
    assert len(mail) == before
    for _ in range(15):
        assert login(client, password='wrong').status_code == 401
    assert login(client).status_code == 429


def test_oauth_unconfigured_and_safe_callback(context):
    client, _, _, _ = context
    if not get_settings().github_client_id:
        assert client.get('/api/v1/auth/providers').json()['github'] is False
        assert client.get('/api/v1/auth/github').status_code == 503
    result = client.get('/api/v1/auth/github/callback?code=fake&state=fake', follow_redirects=False)
    assert result.status_code == 303
    assert 'error=oauth' in result.headers['location']


def test_resend_invalidates_previous_link(context):
    client, _, mail, _ = context
    signup(client, mail, verify=False)
    old = mail[-1][1]
    assert client.post('/api/v1/auth/resend-verification', json={'email': 'developer@example.com'}).status_code == 200
    assert client.post('/api/v1/auth/verify-email', json={'token': old}).status_code == 400
    assert client.post('/api/v1/auth/verify-email', json={'token': mail[-1][1]}).status_code == 200


def test_mail_failure_does_not_leave_partial_account(context, monkeypatch):
    client, db, _, _ = context
    from app.services import identity
    def broken(*args):
        raise OSError('SMTP unavailable')
    monkeypatch.setattr(identity, 'send_action', broken)
    result = client.post('/api/v1/auth/register', json={'email': 'new@example.com', 'password': PASSWORD, 'full_name': 'New User', 'country': 'India'})
    assert result.status_code == 503
    assert db.scalar(select(User).where(User.email == 'new@example.com')) is None


def test_forged_and_database_expired_sessions(context):
    client, db, mail, _ = context
    signup(client, mail); login(client)
    original = client.cookies.get(COOKIE)
    client.cookies.set(COOKIE, original[:-8] + 'forged00', domain='testserver.local', path='/')
    assert client.get('/api/v1/users/me').status_code == 401
    client.cookies.set(COOKIE, original, domain='testserver.local', path='/')
    session = db.scalar(select(UserSession))
    session.expires_at = utcnow() - timedelta(seconds=1)
    db.commit()
    assert client.get('/api/v1/users/me').status_code == 401


def test_oauth_verified_identity_and_no_silent_linking(context, monkeypatch):
    from unittest.mock import AsyncMock
    from app.api.oauth import oauth
    client, db, mail, _ = context
    class ProviderResponse:
        def __init__(self, payload):
            self.payload = payload
        def raise_for_status(self):
            pass
        def json(self):
            return self.payload
    monkeypatch.setattr(oauth.github, 'authorize_access_token', AsyncMock(return_value={'access_token': 'mock-provider-token'}))
    monkeypatch.setattr(oauth.github, 'get', AsyncMock(side_effect=[ProviderResponse({'id': 100, 'name': 'GitHub Developer'}), ProviderResponse([{'email': 'github@example.com', 'primary': True, 'verified': True}])]))
    result = client.get('/api/v1/auth/github/callback?code=test&state=test', follow_redirects=False)
    assert result.status_code == 303
    assert client.get('/api/v1/users/me').json()['email'] == 'github@example.com'
    assert db.scalar(select(User)).github_subject == '100'
    client.post('/api/v1/auth/logout')
    signup(client, mail)
    monkeypatch.setattr(oauth.github, 'get', AsyncMock(side_effect=[ProviderResponse({'id': 101, 'name': 'Different Identity'}), ProviderResponse([{'email': 'developer@example.com', 'primary': True, 'verified': True}])]))
    result = client.get('/api/v1/auth/github/callback?code=test&state=test', follow_redirects=False)
    assert 'error=existing-account' in result.headers['location']
    assert client.get('/api/v1/users/me').status_code == 401


def test_real_redis_rate_limit_expiry():
    from app.core.security import redis_client
    first, second = redis_client(), redis_client()
    key = 'test:rate:' + uuid.uuid4().hex
    script = 'local n=redis.call("INCR",KEYS[1]); if n==1 then redis.call("EXPIRE",KEYS[1],ARGV[1]) end; return n'
    try:
        assert first.eval(script, 1, key, 600) == 1
        assert second.eval(script, 1, key, 600) == 2
        assert 0 < first.ttl(key) <= 600
    finally:
        first.delete(key)
