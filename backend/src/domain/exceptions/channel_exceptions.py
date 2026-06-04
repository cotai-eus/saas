class ChannelError(Exception):
    pass


class ChannelNotFoundError(ChannelError):
    pass


class ChannelNotActiveError(ChannelError):
    pass


class ChannelValidationError(ChannelError):
    pass
