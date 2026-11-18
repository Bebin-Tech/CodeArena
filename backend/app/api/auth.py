import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.core.security import COOKIE, DUMMY_HASH, current_identity, new_session, password_hasher, throttle, utcnow
from app.models import User, UserSession
from app.repositories.users import by_email, public_user
from app.schemas.identity import EmailInput, Login, ProfileInput, Register, ResetPassword, TokenInput, UserPublic, Message, SessionPublic
from app.services.identity import audit, consume_action, issue_action

router = APIRouter()
GENERIC = {'message': 'If this account is eligible, an email will arrive shortly.'}


@router.post('/auth/register', status_code=201, response_model=Message)
def register(payload: Register, request: Request, db=Depends(get_db)):
    throttle(request, 'register', 10)
    # Same response for an existing account; resend is a separate rate-limited flow.
    if by_email(db, payload.email):
        return GENERIC
    user = User(email=payload.email, password_hash=password_hasher.hash(payload.password), full_name=payload.full_name, country=payload.country, institution=payload.institution, role=payload.user_type)
    db.add(user)
    try:
        db.flush()
        issue_action(db, user, 'verify')
        audit(db, 'account.registered', user)
        db.commit()
    except IntegrityError:
        db.rollback()
    return GENERIC


@router.post('/auth/verify-email', response_model=Message)
def verify(payload: TokenInput, request: Request, db=Depends(get_db)):
    throttle(request, 'verify', 30)
    token = consume_action(db, payload.token, 'verify')
    user = db.get(User, token.user_id)
    user.verified = True
    audit(db, 'account.verified', user)
    db.commit()
    return {'message': 'Email verified. You can now sign in.'}


@router.post('/auth/resend-verification', response_model=Message)
def resend(payload: EmailInput, request: Request, db=Depends(get_db)):
    throttle(request, 'email', 5)
    user = by_email(db, payload.email)
    if user and not user.verified and not user.suspended:
        issue_action(db, user, 'verify')
        db.commit()
    return GENERIC


@router.post('/auth/login', response_model=UserPublic)
def login(payload: Login, request: Request, response: Response, db=Depends(get_db)):
    throttle(request, 'login', 15)
    user = db.scalar(select(User).where(User.email == payload.email).with_for_update())
    valid = password_hasher.verify(payload.password, user.password_hash if user and user.password_hash else DUMMY_HASH)
    if not user or not valid or user.suspended:
        audit(db, 'account.login_failed')
        db.commit()
        raise HTTPException(401, 'Email or password is incorrect.')
    if not user.verified:
        raise HTTPException(403, 'Verify your email before signing in.')
    new_session(db, user, request, response)
    audit(db, 'account.login', user)
    db.commit()
    return public_user(user)


@router.post('/auth/logout', response_model=Message)
def logout(response: Response, identity=Depends(current_identity), db=Depends(get_db)):
    user, session = identity
    session.revoked = True
    audit(db, 'account.logout', user)
    db.commit()
    response.delete_cookie(COOKIE, path='/')
    return {'message': 'Signed out.'}


@router.post('/auth/refresh', response_model=UserPublic)
def refresh(request: Request, response: Response, identity=Depends(current_identity), db=Depends(get_db)):
    user, session = identity
    # Serialize renewal: only one replacement session may be issued.
    user = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    locked = db.scalar(select(UserSession).where(UserSession.id == session.id).with_for_update().execution_options(populate_existing=True))
    if locked.revoked or user.suspended:
        raise HTTPException(401, 'Session has already been renewed.')
    locked.revoked = True
    new_session(db, user, request, response)
    audit(db, 'session.renewed', user)
    db.commit()
    return public_user(user)


@router.get('/auth/sessions', response_model=list[SessionPublic])
def sessions(identity=Depends(current_identity), db=Depends(get_db)):
    user, current = identity
    items = db.scalars(select(UserSession).where(UserSession.user_id == user.id, UserSession.revoked.is_(False), UserSession.expires_at > utcnow()).order_by(UserSession.created_at.desc())).all()
    return [{'id': str(s.id), 'created_at': s.created_at.isoformat(), 'expires_at': s.expires_at.isoformat(), 'user_agent': s.user_agent, 'current': s.id == current.id} for s in items]


@router.delete('/auth/sessions/{session_id}', response_model=Message)
def revoke(session_id: uuid.UUID, identity=Depends(current_identity), db=Depends(get_db)):
    session = db.scalar(select(UserSession).where(UserSession.id == session_id, UserSession.user_id == identity[0].id))
    if not session:
        raise HTTPException(404, 'Session not found.')
    session.revoked = True
    audit(db, 'session.revoked', identity[0])
    db.commit()
    return {'message': 'Session revoked.'}


@router.post('/auth/forgot-password', response_model=Message)
def forgot(payload: EmailInput, request: Request, db=Depends(get_db)):
    throttle(request, 'email', 5)
    user = by_email(db, payload.email)
    if user and user.verified and not user.suspended:
        issue_action(db, user, 'reset')
        audit(db, 'password.reset_requested', user)
        db.commit()
    return GENERIC


@router.post('/auth/reset-password', response_model=Message)
def reset(payload: ResetPassword, request: Request, db=Depends(get_db)):
    throttle(request, 'reset', 10)
    token = consume_action(db, payload.token, 'reset')
    user = db.scalar(select(User).where(User.id == token.user_id).with_for_update())
    if user.suspended:
        raise HTTPException(403, 'Account is unavailable.')
    user.password_hash = password_hasher.hash(payload.password)
    db.execute(update(UserSession).where(UserSession.user_id == user.id).values(revoked=True))
    audit(db, 'password.reset', user)
    db.commit()
    return {'message': 'Password updated. Sign in with your new password.'}


@router.get('/users/me', response_model=UserPublic)
def me(identity=Depends(current_identity)):
    return public_user(identity[0])


@router.patch('/users/me/profile', response_model=UserPublic)
def profile(payload: ProfileInput, identity=Depends(current_identity), db=Depends(get_db)):
    user = identity[0]
    for key, value in payload.model_dump().items():
        setattr(user, key, value)
    user.onboarded = True
    audit(db, 'profile.updated', user)
    db.commit()
    return public_user(user)
