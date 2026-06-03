import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    keycloak_realm_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    subscription_plan: Mapped[str] = mapped_column(String(50), server_default="starter")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    users = relationship("User", back_populates="tenant")
    subscription = relationship("Subscription", back_populates="tenant", uselist=False)
    api_keys = relationship("APIKey", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")
    sessions = relationship("Session", back_populates="tenant")
