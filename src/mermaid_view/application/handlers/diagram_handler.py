"""Diagram command and query handlers."""

import base64
from pathlib import Path
from uuid import UUID

from mermaid_view.application.commands.render_diagram import RenderDiagramCommand
from mermaid_view.application.dtos.diagram_dto import (
    DiagramDTO,
    RenderRequestDTO,
    RenderResponseDTO,
)
from mermaid_view.application.queries.get_diagram import GetDiagramQuery
from mermaid_view.domain.entities.diagram import Diagram
from mermaid_view.domain.exceptions import DiagramNotFoundError, RenderError
from mermaid_view.domain.services.diagram_service import DiagramService
from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import OutputFormat, RenderConfig


class DiagramHandler:
    """Handler for diagram-related commands and queries.

    This handler orchestrates the execution of commands and queries
    related to diagrams, using the domain service.
    """

    def __init__(self, diagram_service: DiagramService) -> None:
        """Initialize the handler.

        Args:
            diagram_service: The diagram domain service.
        """
        self._service = diagram_service
        self._diagrams: dict[UUID, Diagram] = {}

    async def handle_render_command(
        self, command: RenderDiagramCommand
    ) -> RenderResponseDTO:
        """Handle a render diagram command.

        Args:
            command: The render command.

        Returns:
            A RenderResponseDTO with the result.
        """
        try:
            # Create render configuration
            config = RenderConfig(
                width=command.width,
                height=command.height,
                theme=command.theme,
                output_format=command.output_format,
                scale=command.scale,
                transparent=command.transparent,
                background_color=command.background_color,
            )

            # Create diagram entity
            diagram = Diagram.create(
                code=command.code,
                config=config,
                name=command.name,
                description=command.description,
            )

            # Store diagram
            self._diagrams[diagram.id] = diagram

            # Render and optionally save
            if command.output_path:
                output_path = await self._service.render_and_save(
                    diagram, command.output_path
                )
                return RenderResponseDTO(
                    success=True,
                    diagram_id=diagram.id,
                    output_path=str(output_path),
                    message=f"Diagram rendered and saved to {output_path}",
                    content_type=self._get_content_type(command.output_format),
                )
            else:
                # Render to memory
                data = await self._service.render_diagram(diagram)
                return RenderResponseDTO(
                    success=True,
                    diagram_id=diagram.id,
                    message="Diagram rendered successfully",
                    data_base64=base64.b64encode(data).decode("utf-8"),
                    content_type=self._get_content_type(command.output_format),
                )

        except RenderError as e:
            return RenderResponseDTO(
                success=False,
                message="Rendering failed",
                error=str(e),
            )
        except Exception as e:
            return RenderResponseDTO(
                success=False,
                message="An error occurred",
                error=str(e),
            )

    async def handle_render_request(
        self, request: RenderRequestDTO
    ) -> RenderResponseDTO:
        """Handle a render request DTO.

        Args:
            request: The render request DTO.

        Returns:
            A RenderResponseDTO with the result.
        """
        command = RenderDiagramCommand.from_dto(request)
        return await self.handle_render_command(command)

    async def handle_get_diagram_query(
        self, query: GetDiagramQuery
    ) -> DiagramDTO:
        """Handle a get diagram query.

        Args:
            query: The get diagram query.

        Returns:
            A DiagramDTO with the diagram data.

        Raises:
            DiagramNotFoundError: If diagram is not found.
        """
        diagram = self._diagrams.get(query.diagram_id)
        if not diagram:
            raise DiagramNotFoundError(f"Diagram {query.diagram_id} not found")
        return DiagramDTO.from_entity(diagram)

    async def render_code_to_bytes(
        self,
        code: str,
        config: RenderConfig | None = None,
    ) -> bytes:
        """Render code directly to bytes.

        Args:
            code: The Mermaid code.
            config: Optional render configuration.

        Returns:
            The rendered image data.

        Raises:
            RenderError: If rendering fails.
        """
        return await self._service.render_code(code, config)

    async def render_code_to_file(
        self,
        code: str,
        output_path: Path,
        config: RenderConfig | None = None,
    ) -> Path:
        """Render code directly to a file.

        Args:
            code: The Mermaid code.
            output_path: The path to save the output.
            config: Optional render configuration.

        Returns:
            The actual path where the file was saved.

        Raises:
            RenderError: If rendering fails.
        """
        return await self._service.render_code_and_save(code, output_path, config)

    def get_diagram(self, diagram_id: UUID) -> Diagram | None:
        """Get a stored diagram by ID.

        Args:
            diagram_id: The diagram ID.

        Returns:
            The diagram if found, None otherwise.
        """
        return self._diagrams.get(diagram_id)

    def list_diagrams(self) -> list[DiagramDTO]:
        """List all stored diagrams.

        Returns:
            A list of DiagramDTOs.
        """
        return [DiagramDTO.from_entity(d) for d in self._diagrams.values()]

    def _get_content_type(self, output_format: OutputFormat) -> str:
        """Get MIME type for output format.

        Args:
            output_format: The output format.

        Returns:
            The MIME type string.
        """
        content_types = {
            OutputFormat.PNG: "image/png",
            OutputFormat.SVG: "image/svg+xml",
            OutputFormat.PDF: "application/pdf",
        }
        return content_types.get(output_format, "application/octet-stream")
