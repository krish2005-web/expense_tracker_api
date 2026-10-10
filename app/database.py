from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# Register model metadata. Do not create tables at import time:
# Alembic imports this module too, and import-time create_all would
# conflict with the initial migration.
from app.models.user import User  # noqa: F401, E402
from app.models.expense import Expense  # noqa: F401, E402

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
