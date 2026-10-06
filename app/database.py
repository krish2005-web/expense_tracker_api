
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base



engine = create_engine(settings.DATABASE_URL)



SessionLocal=sessionmaker(autocommit=False,
                     autoflush=False,
                     bind=engine)

Base=declarative_base()

try:
    with engine.connect() as connection:
        print("Database connected successfully")
except Exception as e:
    print("Database connection failed",e)

def get_db():
    db=SessionLocal()
    try:
        yield db 
    finally:
        db.close()