from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text
from app.api import auth, oauth
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import check_origin, redis_client, require_admin

settings = get_settings()
app = FastAPI(title='CodeArena API', version='0.1.0', description='Milestone 1: identity and account foundation.')
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, session_cookie='codearena_oauth', https_only=settings.secure_cookies, same_site='lax', max_age=600)


@app.middleware('http')
async def security_headers(request: Request, call_next):
    try:
        check_origin(request)
    except HTTPException as error:
        return JSONResponse({'detail': error.detail}, status_code=error.status_code)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Cache-Control'] = 'no-store'
    return response


app.include_router(auth.router, prefix='/api/v1', tags=['Account'])
app.include_router(oauth.router, prefix='/api/v1', tags=['OAuth'])


@app.get('/api/v1/health', tags=['Operations'])
def health(db=Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        redis_client().ping()
    except Exception:
        raise HTTPException(503, 'A required dependency is unavailable.')
    return {'status': 'ok', 'database': 'connected', 'redis': 'connected'}


@app.get('/api/v1/admin/access', tags=['Permissions'])
def admin_access(user=Depends(require_admin)):
    return {'authorized': True, 'role': user.role}
