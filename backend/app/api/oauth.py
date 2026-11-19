from authlib.integrations.starlette_client import OAuth, OAuthError
from httpx import HTTPError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import new_session, throttle
from app.models import User
from app.repositories.users import by_email
from app.services.identity import audit

router = APIRouter()
settings = get_settings()
oauth = OAuth()
oauth.register('github', client_id=settings.github_client_id, client_secret=settings.github_client_secret,
               authorize_url='https://github.com/login/oauth/authorize', access_token_url='https://github.com/login/oauth/access_token',
               api_base_url='https://api.github.com/', client_kwargs={'scope': 'read:user user:email', 'timeout': 10})


@router.get('/auth/providers')
def providers():
    return {'github': bool(settings.github_client_id and settings.github_client_secret), 'email': settings.email_ready}


@router.get('/auth/github')
async def github_start(request: Request):
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(503, 'GitHub sign-in is not configured.')
    throttle(request, 'oauth', 15)
    return await oauth.github.authorize_redirect(request, settings.api_url + '/api/v1/auth/github/callback')


@router.get('/auth/github/callback')
async def github_callback(request: Request, db=Depends(get_db)):
    try:
        token = await oauth.github.authorize_access_token(request)
        profile_response = await oauth.github.get('user', token=token)
        profile_response.raise_for_status()
        profile = profile_response.json()
        emails_response = await oauth.github.get('user/emails', token=token)
        emails_response.raise_for_status()
        emails = emails_response.json()
        email = next((e['email'].lower() for e in emails if e.get('primary') and e.get('verified')), None)
        if not email:
            raise ValueError('A verified primary email is required.')
        subject = str(profile['id'])
    except (OAuthError, HTTPError, ValueError, KeyError):
        return RedirectResponse(settings.frontend_url + '/login?error=oauth', status_code=303)
    user = db.scalar(select(User).where(User.github_subject == subject))
    if not user:
        if by_email(db, email):
            return RedirectResponse(settings.frontend_url + '/login?error=existing-account', status_code=303)
        user = User(email=email, full_name=(profile.get('name') or profile.get('login') or 'Developer')[:120], country='Unspecified', role='developer', verified=True, github_subject=subject)
        db.add(user)
        db.flush()
    if user.suspended:
        raise HTTPException(403, 'Account is unavailable.')
    response = RedirectResponse(settings.frontend_url + '/workspace', status_code=303)
    new_session(db, user, request, response)
    audit(db, 'account.oauth_login', user)
    db.commit()
    return response
