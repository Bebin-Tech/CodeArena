import uuid
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db
from app.main import app


@pytest.fixture(scope='session')
def database_engine():
    # Dedicated random schema: no deletion or modification of application data.
    engine = create_engine(get_settings().db_url, connect_args={'connect_timeout': 10})
    schema = 'codearena_test_' + uuid.uuid4().hex
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA {schema}'))
        connection.execute(text(f'SET search_path TO {schema}'))
        config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
        config.attributes['connection'] = connection
        command.upgrade(config, 'head')
    yield engine, schema
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA {schema} CASCADE'))
    engine.dispose()


class Counters:
    def __init__(self):
        self.values = {}

    def eval(self, script, numkeys, key, ttl):
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]


@pytest.fixture
def context(database_engine, monkeypatch):
    from app.core import security
    from app.services import identity
    engine, schema = database_engine
    with engine.connect() as connection:
        transaction = connection.begin()
        connection.execute(text(f'SET LOCAL search_path TO {schema}'))
        db = Session(bind=connection, join_transaction_mode='create_savepoint', expire_on_commit=False)
        app.dependency_overrides[get_db] = lambda: db
        mail = []
        monkeypatch.setattr(identity, 'send_action', lambda email, token, purpose: mail.append((email, token, purpose)))
        counters = Counters()
        monkeypatch.setattr(security, 'redis_client', lambda: counters)
        with TestClient(app, headers={'Origin': get_settings().frontend_url}) as client:
            yield client, db, mail, counters
        app.dependency_overrides.clear()
        db.close()
        transaction.rollback()
