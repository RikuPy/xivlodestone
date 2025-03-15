class LodestoneError(Exception):
    """Base exception for all Lodestone-related errors."""
    ...


class NotFoundError(LodestoneError):
    """Thrown when a requested resource (such as a character or free company) cannot be found."""
    ...
