from enum import Enum


class ChannelType(str, Enum):
    WHATSAPP_OFFICIAL = "whatsapp_official"
    WHATSAPP_UNOFFICIAL = "whatsapp_unofficial"
    FACEBOOK_MESSENGER = "facebook_messenger"
    INSTAGRAM_CHAT = "instagram_chat"
    TELEGRAM = "telegram"


class MessageStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    RECEIVED = "received"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    TEMPLATE = "template"
    BUTTONS = "buttons"
