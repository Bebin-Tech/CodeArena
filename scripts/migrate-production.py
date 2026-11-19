"""Apply migrations using explicitly injected hosted credentials, never local .env defaults.

Run with: vercel env run -e production -- .venv/Scripts/python.exe scripts/migrate-production.py
"""
import os
from pathlib import Path
from urllib.parse import urlsplit
from alembic import command
from alembic.config import Config

database_url = os.environ.get('DATABASE_URL_UNPOOLED') or os.environ.get('DATABASE_URL')
if not database_url:
    raise SystemExit('Refusing migration: hosted DATABASE_URL is not injected.')
host = urlsplit(database_url).hostname
if not host or host in {'localhost', '127.0.0.1', '::1'}:
    raise SystemExit('Refusing production migration against a local database.')
os.environ['DATABASE_URL'] = database_url
root = Path(__file__).resolve().parents[1]
command.upgrade(Config(str(root / 'backend' / 'alembic.ini')), 'head')
print('Hosted database migration completed.')
