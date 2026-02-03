"""Domain ports (interfaces)."""

from .renderer import IRenderPort
from .storage import IStoragePort

__all__ = ["IRenderPort", "IStoragePort"]
