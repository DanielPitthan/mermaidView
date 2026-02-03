"""Domain exceptions for MermaidView."""


class MermaidViewError(Exception):
    """Base exception for MermaidView application."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidMermaidCodeError(MermaidViewError):
    """Raised when Mermaid code is invalid."""

    pass


class RenderError(MermaidViewError):
    """Raised when diagram rendering fails."""

    pass


class StorageError(MermaidViewError):
    """Raised when storage operations fail."""

    pass


class DiagramNotFoundError(MermaidViewError):
    """Raised when a diagram is not found."""

    pass


class ConfigurationError(MermaidViewError):
    """Raised when configuration is invalid."""

    pass


class BrowserError(RenderError):
    """Raised when browser operations fail."""

    pass


class TimeoutError(RenderError):
    """Raised when rendering times out."""

    pass


class NetworkError(MermaidViewError):
    """Raised when network operations fail."""

    pass
