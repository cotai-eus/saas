from domain.value_objects.channel_type import ChannelType
from .base import ChannelProvider
from .whatsapp_cloud import WhatsAppCloudProvider
from .whatsapp_baileys import WhatsAppBaileysProvider
from .facebook import FacebookProvider
from .instagram import InstagramProvider
from .telegram import TelegramProvider

_REGISTRY: dict[ChannelType, ChannelProvider] = {
    ChannelType.WHATSAPP_OFFICIAL: WhatsAppCloudProvider(),
    ChannelType.WHATSAPP_UNOFFICIAL: WhatsAppBaileysProvider(),
    ChannelType.FACEBOOK_MESSENGER: FacebookProvider(),
    ChannelType.INSTAGRAM_CHAT: InstagramProvider(),
    ChannelType.TELEGRAM: TelegramProvider(),
}


class ProviderFactory:
    @staticmethod
    def get(channel_type: ChannelType) -> ChannelProvider:
        provider = _REGISTRY.get(channel_type)
        if not provider:
            raise ValueError(f"Provider not registered: {channel_type}")
        return provider

    @staticmethod
    def register(channel_type: ChannelType, provider: ChannelProvider) -> None:
        _REGISTRY[channel_type] = provider
