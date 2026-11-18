import secrets
from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy import select, update
from app.core.security import token_digest, utcnow
from app.models import ActionToken, AuditLog
from app.services.mail import send_action


def audit(db, event, user=None):
    db.add(AuditLog(event=event, user_id=user.id if user else None))


def issue_action(db, user, purpose):
    raw = secrets.token_urlsafe(32)
    db.execute(update(ActionToken).where(ActionToken.user_id == user.id, ActionToken.purpose == purpose, ActionToken.consumed.is_(False)).values(consumed=True))
    db.add(ActionToken(user_id=user.id, digest=token_digest(raw), purpose=purpose, expires_at=utcnow() + timedelta(minutes=30)))
    try:
        send_action(user.email, raw, purpose)
    except Exception as error:
        db.rollback()
        raise HTTPException(503, 'Email delivery is unavailable. Please retry later.') from error


def consume_action(db, raw, purpose):
    token = db.scalar(select(ActionToken).where(ActionToken.digest == token_digest(raw), ActionToken.purpose == purpose).with_for_update())
    if not token or token.consumed or token.expires_at <= utcnow():
        raise HTTPException(400, 'This link is invalid or expired. Request a new one.')
    token.consumed = True
    return token
