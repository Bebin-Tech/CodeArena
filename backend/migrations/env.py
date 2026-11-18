from alembic import context
from app.core.config import get_settings
from app.core.database import Base
from app.models import User, UserSession, ActionToken, AuditLog
from sqlalchemy import create_engine

target_metadata = Base.metadata
if context.is_offline_mode():
    context.configure(url=get_settings().db_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    existing = context.config.attributes.get('connection')
    if existing is not None:
        context.configure(connection=existing, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    else:
        with create_engine(get_settings().db_url).connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
