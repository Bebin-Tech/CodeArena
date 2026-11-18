from sqlalchemy import select
from app.models import User


def by_email(db, email):
    return db.scalar(select(User).where(User.email == email.lower()))


def public_user(user):
    return dict(id=str(user.id), email=user.email, full_name=user.full_name,
                role=user.role, country=user.country, institution=user.institution,
                bio=user.bio, verified=user.verified, onboarded=user.onboarded,
                created_at=user.created_at.isoformat())
