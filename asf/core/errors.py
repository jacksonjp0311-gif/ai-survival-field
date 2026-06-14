class ASFError(Exception):
    """Base ASF runtime error."""


class PolicyError(ASFError):
    """Policy loading or validation failed."""

