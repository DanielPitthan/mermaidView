"""Renderer port interface."""

from abc import ABC, abstractmethod

from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import RenderConfig


class IRenderPort(ABC):
    """Interface for diagram rendering adapters.

    This port defines the contract for rendering Mermaid diagrams
    to various output formats. Implementations can use different
    rendering strategies (Playwright, mermaid.ink, etc.).
    """

    @abstractmethod
    async def render_to_png(self, code: MermaidCode, config: RenderConfig) -> bytes:
        """Render Mermaid code to PNG format.

        Args:
            code: The Mermaid code to render.
            config: Rendering configuration.

        Returns:
            PNG image data as bytes.

        Raises:
            RenderError: If rendering fails.
        """
        pass

    @abstractmethod
    async def render_to_svg(self, code: MermaidCode, config: RenderConfig) -> bytes:
        """Render Mermaid code to SVG format.

        Args:
            code: The Mermaid code to render.
            config: Rendering configuration.

        Returns:
            SVG data as bytes.

        Raises:
            RenderError: If rendering fails.
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the renderer is available.

        Returns:
            True if the renderer can be used.
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the renderer.

        This should be called before using the renderer.

        Raises:
            RenderError: If initialization fails.
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup renderer resources.

        This should be called when the renderer is no longer needed.
        """
        pass

    async def __aenter__(self) -> "IRenderPort":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.cleanup()
