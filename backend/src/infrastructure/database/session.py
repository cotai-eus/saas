import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(
    os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('DB_USER', 'saas')}:{os.getenv('DB_PASSWORD', '')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME', 'saas')}",
    ),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionFactory = sessionmaker(bind=engine)
SessionLocal = scoped_session(SessionFactory)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        SessionLocal.remove()