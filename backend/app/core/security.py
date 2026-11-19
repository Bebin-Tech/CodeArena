import hashlib
import ipaddress
import os
import uuid
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyCookie
from redis import Redis
from sqlalchemy import select
from app.core.config import get_settings
from app.core.database import get_db
from app.models import User, UserSession

password_hasher = PasswordHash.recommended()
DUMMY_HASH = password_hasher.hash('constant-time-fallback-not-a-credential')
COOKIE = 'codearena_session'
cookie_auth = APIKeyCookie(name=COOKIE, auto_error=False)


def utcnow():
    return datetime.now(timezone.utc)


def token_digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def check_origin(request: Request):
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        if request.headers.get('origin') != get_settings().frontend_url:
            raise HTTPException(403, 'Request origin is not allowed.')


def redis_client():
    return Redis.from_url(get_settings().redis_url, socket_connect_timeout=2, socket_timeout=2)


def throttle(request: Request, bucket: str, limit=10):
    # Vercel overwrites this header at ingress. Never trust it in local/direct deployments.
    host = request.client.host if request.client else 'unknown'
    if os.environ.get('VERCEL') == '1':
        forwarded = request.headers.get('x-vercel-forwarded-for', '').split(',')[0].strip()
        try:
            host = str(ipaddress.ip_address(forwarded))
        except ValueError:
            pass
    key = f'rate:{bucket}:{host}'
    try:
        count = redis_client().eval('local n=redis.call("INCR",KEYS[1]); if n==1 then redis.call("EXPIRE",KEYS[1],ARGV[1]) end; return n', 1, key, 600)
    except Exception:
        raise HTTPException(503, 'Authentication is temporarily unavailable. Please retry.')
    if count > limit:
        raise HTTPException(429, 'Too many attempts. Try again in ten minutes.', headers={'Retry-After': '600'})


def new_session(db, user, request, response):
    settings = get_settings()
    expiry = utcnow() + timedelta(minutes=settings.session_minutes)
    session = UserSession(user_id=user.id, expires_at=expiry, user_agent=request.headers.get('user-agent', '')[:240])
    db.add(session)
    db.flush()
    token = jwt.encode({'sub': str(user.id), 'sid': str(session.id), 'exp': expiry, 'iat': utcnow(), 'iss': 'codearena', 'aud': 'codearena-web'}, settings.secret_key, algorithm='HS256')
    response.set_cookie(COOKIE, token, max_age=settings.session_minutes * 60, httponly=True, secure=settings.secure_cookies, samesite='lax', path='/')
    return session


def current_identity(request: Request, db=Depends(get_db), cookie: str | None = Security(cookie_auth)):
    try:
        claims = jwt.decode(cookie or '', get_settings().secret_key, algorithms=['HS256'], issuer='codearena', audience='codearena-web', options={'require': ['exp', 'iat', 'sub', 'sid']})
        session = db.scalar(select(UserSession).where(UserSession.id == uuid.UUID(claims['sid'])))
        user = db.get(User, uuid.UUID(claims['sub']))
        if not session or session.revoked or session.user_id != user.id or session.expires_at <= utcnow() or not user.verified or user.suspended:
            raise ValueError()
        return user, session
    except (jwt.PyJWTError, ValueError, AttributeError, TypeError, KeyError):
        raise HTTPException(401, 'Please sign in to continue.')


def require_admin(identity=Depends(current_identity)):
    if identity[0].role not in ('super_admin', 'platform_admin'):
        raise HTTPException(403, 'Administrator permission is required.')
    return identity[0]
