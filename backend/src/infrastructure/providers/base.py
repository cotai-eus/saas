from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from domain.entities.channel import Channel
from domain.entities.message import Message


@dataclass
class SendResult:
    success: bool
    provider_message_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    raw_response: dict = field(default_factory=dict)


class ChannelProvider(ABC):
    @abstractmethod
    def send(self, channel: Channel, message: Message) -> SendResult:
        ...

    @abstractmethod
    def validate(self, channel: Channel) -> bool:
        ...

    @abstractmethod
    def parse_inbound(self, payload: dict, headers: dict) -> list[Message]:
        ...

    @abstractmethod
    def parse_status(self, payload: dict) -> list[dict]:
        ...
