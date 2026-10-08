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

# Import models after Base is created so metadata knows all tables.
from app.models.user import User  # noqa: F401, E402
from app.models.expense import Expense  # noqa: F401, E402

try:
    with engine.connect():
        print("Database connected successfully")

    # Render demo deployment uses SQLite when DATABASE_URL is not provided.
    # Create the tables automatically so the demo works even when the
    # existing Render service has not applied the Alembic build command.
    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        print("SQLite tables ready")
except Exception as exc:
    print("Database connection failed:", exc)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
