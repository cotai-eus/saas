import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, text, Boolean, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.base import Base

class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column()
    enabled: Mapped[bool] = mapped_column(Boolean, server_default="FALSE")
    rollout_percentage: Mapped[int] = mapped_column(Integer, server_default="0")
    allowed_tenants: Mapped[List[str]] = mapped_column(ARRAY(String), server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
