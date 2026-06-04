from dataclasses import dataclass, field
from domain.value_objects.channel_type import ContentType


@dataclass
class MessageContent:
    type: ContentType
    text: str | None = None
    media_url: str | None = None
    template_name: str | None = None
    template_vars: dict = field(default_factory=dict)
