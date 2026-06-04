from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Contact:
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = None
    channel_id: UUID = None
    external_id: str = None
    name: str = ""
    phone: str = None
    avatar_url: str = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = None
