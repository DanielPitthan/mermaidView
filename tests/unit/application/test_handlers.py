"""Unit tests for application layer handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from pathlib import Path

from mermaid_view.application.commands.render_diagram import RenderDiagramCommand
from mermaid_view.application.queries.get_diagram import GetDiagramQuery
from mermaid_view.application.dtos.diagram_dto import (
    DiagramDTO,
    RenderRequestDTO,
    RenderResponseDTO,
)
from mermaid_view.application.handlers.diagram_handler import DiagramHandler
from mermaid_view.domain.entities.diagram import Diagram
from mermaid_view.domain.exceptions import DiagramNotFoundError, RenderError
from mermaid_view.domain.services.diagram_service import DiagramService
from mermaid_view.domain.value_objects.render_config import OutputFormat, RenderConfig, Theme


class TestRenderDiagramCommand:
    """Tests for RenderDiagramCommand."""

    def test_create_command(self):
        """Test creating a render command."""
        command = RenderDiagramCommand(
            code="graph TD; A-->B",
            output_path=Path("output.png"),
            width=1000,
            height=800,
        )
        
        assert command.code == "graph TD; A-->B"
        assert command.output_path == Path("output.png")
        assert command.width == 1000
        assert command.height == 800

    def test_command_validation_empty_code(self):
        """Test that empty code raises ValueError."""
        with pytest.raises(ValueError):
            RenderDiagramCommand(code="")

    def test_command_validation_invalid_width(self):
        """Test that invalid width raises ValueError."""
        with pytest.raises(ValueError):
            RenderDiagramCommand(code="graph TD; A-->B", width=0)

    def test_command_validation_invalid_height(self):
        """Test that invalid height raises ValueError."""
        with pytest.raises(ValueError):
            RenderDiagramCommand(code="graph TD; A-->B", height=-100)

    def test_command_from_dto(self):
        """Test creating command from DTO."""
        dto = RenderRequestDTO(
            code="graph TD; A-->B",
            output_path="output.png",
            width=1200,
            height=800,
            theme=Theme.DARK,
        )
        
        command = RenderDiagramCommand.from_dto(dto)
        
        assert command.code == "graph TD; A-->B"
        assert command.output_path == Path("output.png")
        assert command.width == 1200
        assert command.theme == Theme.DARK


class TestGetDiagramQuery:
    """Tests for GetDiagramQuery."""

    def test_create_query(self):
        """Test creating a get diagram query."""
        diagram_id = uuid4()
        query = GetDiagramQuery(diagram_id=diagram_id)
        
        assert query.diagram_id == diagram_id

    def test_query_from_string(self):
        """Test creating query from string ID."""
        id_str = "12345678-1234-5678-1234-567812345678"
        query = GetDiagramQuery.from_string(id_str)
        
        assert str(query.diagram_id) == id_str

    def test_query_from_invalid_string(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            GetDiagramQuery.from_string("invalid-uuid")


class TestRenderRequestDTO:
    """Tests for RenderRequestDTO."""

    def test_create_dto(self):
        """Test creating a render request DTO."""
        dto = RenderRequestDTO(
            code="graph TD; A-->B",
            width=1000,
            height=800,
        )
        
        assert dto.code == "graph TD; A-->B"
        assert dto.width == 1000
        assert dto.height == 800
        assert dto.theme == Theme.DEFAULT
        assert dto.output_format == OutputFormat.PNG

    def test_dto_validation_empty_code(self):
        """Test that empty code raises ValidationError."""
        with pytest.raises(ValueError):
            RenderRequestDTO(code="")

    def test_dto_validation_width_range(self):
        """Test width validation range."""
        with pytest.raises(ValueError):
            RenderRequestDTO(code="graph TD", width=50)  # Too small
        
        with pytest.raises(ValueError):
            RenderRequestDTO(code="graph TD", width=5000)  # Too large

    def test_dto_code_normalization(self):
        """Test that code is normalized (stripped)."""
        dto = RenderRequestDTO(code="  graph TD; A-->B  ")
        assert dto.code == "graph TD; A-->B"


class TestRenderResponseDTO:
    """Tests for RenderResponseDTO."""

    def test_success_response(self):
        """Test creating a success response."""
        response = RenderResponseDTO(
            success=True,
            diagram_id=uuid4(),
            output_path="output.png",
            message="Rendered successfully",
        )
        
        assert response.success is True
        assert response.error is None

    def test_error_response(self):
        """Test creating an error response."""
        response = RenderResponseDTO(
            success=False,
            message="Rendering failed",
            error="Browser timeout",
        )
        
        assert response.success is False
        assert response.error == "Browser timeout"


class TestDiagramDTO:
    """Tests for DiagramDTO."""

    def test_from_entity(self):
        """Test creating DTO from Diagram entity."""
        diagram = Diagram.create(
            code="graph TD; A-->B",
            name="Test Diagram",
        )
        
        dto = DiagramDTO.from_entity(diagram)
        
        assert dto.id == diagram.id
        assert dto.code == "graph TD; A-->B"
        assert dto.diagram_type == "flowchart"
        assert dto.name == "Test Diagram"
        assert dto.is_rendered is False


class TestDiagramHandler:
    """Tests for DiagramHandler."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock diagram service."""
        service = MagicMock(spec=DiagramService)
        service.render_diagram = AsyncMock(return_value=b"PNG data")
        service.render_code = AsyncMock(return_value=b"PNG data")
        service.render_and_save = AsyncMock(return_value=Path("output.png"))
        service.render_code_and_save = AsyncMock(return_value=Path("output.png"))
        return service

    @pytest.fixture
    def handler(self, mock_service):
        """Create a handler with mock service."""
        return DiagramHandler(mock_service)

    @pytest.mark.asyncio
    async def test_handle_render_command_to_memory(self, handler, mock_service):
        """Test handling render command without output path."""
        command = RenderDiagramCommand(code="graph TD; A-->B")
        
        response = await handler.handle_render_command(command)
        
        assert response.success is True
        assert response.diagram_id is not None
        assert response.data_base64 is not None
        mock_service.render_diagram.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_render_command_to_file(self, handler, mock_service):
        """Test handling render command with output path."""
        command = RenderDiagramCommand(
            code="graph TD; A-->B",
            output_path=Path("output.png"),
        )
        
        response = await handler.handle_render_command(command)
        
        assert response.success is True
        assert response.output_path == "output.png"
        mock_service.render_and_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_render_command_error(self, handler, mock_service):
        """Test handling render command when rendering fails."""
        mock_service.render_diagram.side_effect = RenderError("Browser failed")
        command = RenderDiagramCommand(code="graph TD; A-->B")
        
        response = await handler.handle_render_command(command)
        
        assert response.success is False
        assert "Browser failed" in response.error

    @pytest.mark.asyncio
    async def test_handle_render_request(self, handler, mock_service):
        """Test handling render request DTO."""
        request = RenderRequestDTO(code="graph TD; A-->B")
        
        response = await handler.handle_render_request(request)
        
        assert response.success is True

    @pytest.mark.asyncio
    async def test_handle_get_diagram_query_found(self, handler):
        """Test getting an existing diagram."""
        # First render to store a diagram
        command = RenderDiagramCommand(code="graph TD; A-->B")
        await handler.handle_render_command(command)
        
        # Get the stored diagram
        diagrams = handler.list_diagrams()
        assert len(diagrams) == 1
        
        diagram_id = diagrams[0].id
        query = GetDiagramQuery(diagram_id=diagram_id)
        
        result = await handler.handle_get_diagram_query(query)
        
        assert result.id == diagram_id

    @pytest.mark.asyncio
    async def test_handle_get_diagram_query_not_found(self, handler):
        """Test getting a non-existent diagram."""
        query = GetDiagramQuery(diagram_id=uuid4())
        
        with pytest.raises(DiagramNotFoundError):
            await handler.handle_get_diagram_query(query)

    @pytest.mark.asyncio
    async def test_render_code_to_bytes(self, handler, mock_service):
        """Test rendering code directly to bytes."""
        result = await handler.render_code_to_bytes("graph TD; A-->B")
        
        assert result == b"PNG data"
        mock_service.render_code.assert_called_once()

    @pytest.mark.asyncio
    async def test_render_code_to_file(self, handler, mock_service):
        """Test rendering code directly to file."""
        result = await handler.render_code_to_file(
            "graph TD; A-->B",
            Path("output.png"),
        )
        
        assert result == Path("output.png")
        mock_service.render_code_and_save.assert_called_once()

    def test_list_diagrams_empty(self, handler):
        """Test listing diagrams when empty."""
        diagrams = handler.list_diagrams()
        assert diagrams == []

    @pytest.mark.asyncio
    async def test_list_diagrams_with_items(self, handler, mock_service):
        """Test listing diagrams after rendering."""
        # Render a few diagrams
        await handler.handle_render_command(
            RenderDiagramCommand(code="graph TD; A-->B")
        )
        await handler.handle_render_command(
            RenderDiagramCommand(code="sequenceDiagram\nAlice->>Bob: Hi")
        )
        
        diagrams = handler.list_diagrams()
        
        assert len(diagrams) == 2

    def test_get_diagram_direct(self, handler):
        """Test getting diagram directly by ID."""
        result = handler.get_diagram(uuid4())
        assert result is None
