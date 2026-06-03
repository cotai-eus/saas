import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, text, ForeignKey, Boolean, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.base import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    scopes: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    rate_limit: Mapped[int] = mapped_column(Integer, server_default="1000")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="TRUE")
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    tenant = relationship("Tenant", back_populates="api_keys")
