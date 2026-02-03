"""Domain service for diagram operations."""

from pathlib import Path

from mermaid_view.domain.entities.diagram import Diagram
from mermaid_view.domain.exceptions import RenderError
from mermaid_view.domain.ports.renderer import IRenderPort
from mermaid_view.domain.ports.storage import IStoragePort
from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import OutputFormat, RenderConfig


class DiagramService:
    """Domain service for diagram-related operations.

    This service orchestrates the rendering and storage of diagrams
    using the provided ports (adapters).
    """

    def __init__(
        self,
        renderer: IRenderPort,
        storage: IStoragePort,
        fallback_renderer: IRenderPort | None = None,
    ) -> None:
        """Initialize the diagram service.

        Args:
            renderer: The primary renderer port.
            storage: The storage port.
            fallback_renderer: Optional fallback renderer.
        """
        self._renderer = renderer
        self._storage = storage
        self._fallback_renderer = fallback_renderer

    async def render_diagram(self, diagram: Diagram) -> bytes:
        """Render a diagram to its configured output format.

        Args:
            diagram: The diagram to render.

        Returns:
            The rendered diagram data.

        Raises:
            RenderError: If rendering fails.
        """
        renderer = self._renderer

        # Check if primary renderer is available
        if not await renderer.is_available():
            if self._fallback_renderer and await self._fallback_renderer.is_available():
                renderer = self._fallback_renderer
            else:
                raise RenderError("No renderer available")

        # Render based on output format
        if diagram.config.output_format == OutputFormat.SVG:
            data = await renderer.render_to_svg(diagram.code, diagram.config)
        else:
            data = await renderer.render_to_png(diagram.code, diagram.config)

        # Update diagram with rendered data
        diagram.set_rendered_data(data)

        return data

    async def render_code(
        self,
        code: str | MermaidCode,
        config: RenderConfig | None = None,
    ) -> bytes:
        """Render Mermaid code directly.

        Args:
            code: The Mermaid code to render.
            config: Optional render configuration.

        Returns:
            The rendered diagram data.

        Raises:
            RenderError: If rendering fails.
        """
        if isinstance(code, str):
            mermaid_code = MermaidCode.create(code)
        else:
            mermaid_code = code

        render_config = config or RenderConfig.default()
        renderer = self._renderer

        # Check if primary renderer is available
        if not await renderer.is_available():
            if self._fallback_renderer and await self._fallback_renderer.is_available():
                renderer = self._fallback_renderer
            else:
                raise RenderError("No renderer available")

        # Render based on output format
        if render_config.output_format == OutputFormat.SVG:
            return await renderer.render_to_svg(mermaid_code, render_config)
        else:
            return await renderer.render_to_png(mermaid_code, render_config)

    async def render_and_save(
        self,
        diagram: Diagram,
        output_path: Path,
    ) -> Path:
        """Render a diagram and save to file.

        Args:
            diagram: The diagram to render.
            output_path: The path to save the output.

        Returns:
            The actual path where the file was saved.

        Raises:
            RenderError: If rendering fails.
            StorageError: If saving fails.
        """
        # Render the diagram
        data = await self.render_diagram(diagram)

        # Ensure output directory exists
        await self._storage.ensure_directory(output_path.parent)

        # Save to file
        return await self._storage.save_rendered_output(data, output_path)

    async def render_code_and_save(
        self,
        code: str | MermaidCode,
        output_path: Path,
        config: RenderConfig | None = None,
    ) -> Path:
        """Render code directly and save to file.

        Args:
            code: The Mermaid code to render.
            output_path: The path to save the output.
            config: Optional render configuration.

        Returns:
            The actual path where the file was saved.

        Raises:
            RenderError: If rendering fails.
            StorageError: If saving fails.
        """
        # Render the code
        data = await self.render_code(code, config)

        # Ensure output directory exists
        await self._storage.ensure_directory(output_path.parent)

        # Save to file
        return await self._storage.save_rendered_output(data, output_path)

    async def save_diagram(self, diagram: Diagram) -> None:
        """Save a diagram entity.

        Args:
            diagram: The diagram to save.

        Raises:
            StorageError: If saving fails.
        """
        await self._storage.save_diagram(diagram)

    async def initialize(self) -> None:
        """Initialize the service and its dependencies."""
        await self._renderer.initialize()
        if self._fallback_renderer:
            try:
                await self._fallback_renderer.initialize()
            except Exception:
                # Fallback renderer initialization failure is not critical
                pass

    async def cleanup(self) -> None:
        """Cleanup service resources."""
        await self._renderer.cleanup()
        if self._fallback_renderer:
            try:
                await self._fallback_renderer.cleanup()
            except Exception:
                pass

    async def __aenter__(self) -> "DiagramService":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.cleanup()
