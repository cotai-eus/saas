from fastapi import Request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from infrastructure.settings import settings

engine = create_engine(
    settings.resolved_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionFactory = sessionmaker(bind=engine)
SessionLocal = scoped_session(SessionFactory)


def get_db(request: Request):
    tenant_id = getattr(request.state, "tenant_id", None)
    db = SessionLocal()
    try:
        if tenant_id:
            db.execute(
                text("SELECT set_config('app.current_tenant_id', :tid, true)"),
                {"tid": str(tenant_id)},
            )
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        SessionLocal.remove()
