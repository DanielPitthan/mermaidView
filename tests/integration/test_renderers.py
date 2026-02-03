"""Integration tests for renderers."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import RenderConfig, Theme, OutputFormat
from mermaid_view.domain.exceptions import RenderError
from mermaid_view.infrastructure.adapters.playwright_renderer import PlaywrightRenderer
from mermaid_view.infrastructure.adapters.mermaid_ink_renderer import MermaidInkRenderer
from mermaid_view.infrastructure.adapters.file_storage import FileStorage


class TestPlaywrightRenderer:
    """Integration tests for PlaywrightRenderer."""

    @pytest.fixture
    def renderer(self):
        """Create a Playwright renderer instance."""
        return PlaywrightRenderer(timeout=30000, headless=True)

    @pytest.mark.asyncio
    async def test_is_available(self, renderer):
        """Test that Playwright availability check works."""
        # This will return True if playwright is installed
        result = await renderer.is_available()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_render_flowchart_to_png(self, renderer, sample_flowchart_code):
        """Test rendering flowchart to PNG (requires Playwright)."""
        pytest.importorskip("playwright")
        
        code = MermaidCode.create(sample_flowchart_code)
        config = RenderConfig.for_png()

        async with renderer:
            result = await renderer.render_to_png(code, config)

        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG magic number
        assert result[:4] == b'\x89PNG'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_render_sequence_to_png(self, renderer, sample_sequence_code):
        """Test rendering sequence diagram to PNG (requires Playwright)."""
        pytest.importorskip("playwright")
        
        code = MermaidCode.create(sample_sequence_code)
        config = RenderConfig.for_png(theme=Theme.DARK)

        async with renderer:
            result = await renderer.render_to_png(code, config)

        assert isinstance(result, bytes)
        assert result[:4] == b'\x89PNG'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_render_to_svg(self, renderer, sample_flowchart_code):
        """Test rendering to SVG (requires Playwright)."""
        pytest.importorskip("playwright")
        
        code = MermaidCode.create(sample_flowchart_code)
        config = RenderConfig.for_svg()

        async with renderer:
            result = await renderer.render_to_svg(code, config)

        assert isinstance(result, bytes)
        svg_str = result.decode('utf-8')
        assert '<svg' in svg_str
        assert '</svg>' in svg_str

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_render_with_different_themes(self, renderer, sample_flowchart_code):
        """Test rendering with different themes (requires Playwright)."""
        pytest.importorskip("playwright")
        
        code = MermaidCode.create(sample_flowchart_code)
        themes = [Theme.DEFAULT, Theme.DARK, Theme.FOREST, Theme.NEUTRAL]

        async with renderer:
            for theme in themes:
                config = RenderConfig.for_png(theme=theme)
                result = await renderer.render_to_png(code, config)
                assert isinstance(result, bytes)
                assert len(result) > 0

    @pytest.mark.asyncio
    async def test_cleanup_without_initialize(self, renderer):
        """Test cleanup can be called without initialize."""
        # Should not raise
        await renderer.cleanup()


class TestMermaidInkRenderer:
    """Integration tests for MermaidInkRenderer."""

    @pytest.fixture
    def renderer(self):
        """Create a Mermaid.ink renderer instance."""
        return MermaidInkRenderer(timeout=30.0)

    @pytest.mark.asyncio
    async def test_is_available(self, renderer):
        """Test mermaid.ink availability check."""
        result = await renderer.is_available()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_render_flowchart_to_png(self, renderer, sample_flowchart_code):
        """Test rendering flowchart to PNG via mermaid.ink."""
        code = MermaidCode.create(sample_flowchart_code)
        config = RenderConfig.for_png()

        async with renderer:
            if not await renderer.is_available():
                pytest.skip("mermaid.ink service not available")
            
            result = await renderer.render_to_png(code, config)

        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_render_to_svg(self, renderer, sample_flowchart_code):
        """Test rendering to SVG via mermaid.ink."""
        code = MermaidCode.create(sample_flowchart_code)
        config = RenderConfig.for_svg()

        async with renderer:
            if not await renderer.is_available():
                pytest.skip("mermaid.ink service not available")
            
            result = await renderer.render_to_svg(code, config)

        assert isinstance(result, bytes)
        svg_str = result.decode('utf-8')
        assert '<svg' in svg_str.lower() or 'svg' in svg_str.lower()

    def test_encode_diagram(self, renderer):
        """Test diagram encoding."""
        code = "graph TD; A-->B"
        encoded = renderer._encode_diagram(code)
        
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        # URL-safe base64 characters only
        assert all(c.isalnum() or c in '-_' for c in encoded)

    def test_build_params(self, renderer):
        """Test building query parameters."""
        config = RenderConfig(
            width=1200,
            height=800,
            theme=Theme.DARK,
            scale=2.0,
        )
        
        params = renderer._build_params(config, OutputFormat.PNG)
        
        assert "theme" in params
        assert params["theme"] == "dark"
        assert "width" in params
        assert "scale" in params


class TestFileStorage:
    """Integration tests for FileStorage."""

    @pytest.fixture
    def storage(self, temp_output_dir, temp_diagrams_dir):
        """Create a FileStorage instance with temp directories."""
        return FileStorage(
            base_path=temp_output_dir.parent,
            output_dir=temp_output_dir.name,
            diagrams_dir=temp_diagrams_dir.name,
        )

    @pytest.mark.asyncio
    async def test_save_rendered_output(self, storage, temp_output_dir):
        """Test saving rendered output to file."""
        data = b'\x89PNG\r\n\x1a\n' + b'fake png data'
        output_path = Path("test_diagram.png")

        result = await storage.save_rendered_output(data, output_path)

        assert result.exists()
        assert result.read_bytes() == data

    @pytest.mark.asyncio
    async def test_read_file(self, storage, temp_output_dir):
        """Test reading a file."""
        # Create a test file
        test_file = temp_output_dir / "test.txt"
        test_content = b"test content"
        test_file.write_bytes(test_content)

        result = await storage.read_file(test_file)

        assert result == test_content

    @pytest.mark.asyncio
    async def test_file_exists(self, storage, temp_output_dir):
        """Test file existence check."""
        # Create a test file
        test_file = temp_output_dir / "exists.txt"
        test_file.write_text("test")

        assert await storage.file_exists(test_file) is True
        assert await storage.file_exists(temp_output_dir / "not_exists.txt") is False

    @pytest.mark.asyncio
    async def test_ensure_directory(self, storage, temp_output_dir):
        """Test directory creation."""
        new_dir = temp_output_dir / "new_subdir"
        
        await storage.ensure_directory(new_dir)
        
        assert new_dir.exists()
        assert new_dir.is_dir()

    @pytest.mark.asyncio
    async def test_save_and_get_diagram(self, storage, sample_flowchart_code):
        """Test saving and retrieving a diagram."""
        from mermaid_view.domain.entities.diagram import Diagram
        
        diagram = Diagram.create(
            code=sample_flowchart_code,
            name="Test Diagram",
            description="A test diagram",
        )

        await storage.save_diagram(diagram)
        
        # Retrieve
        retrieved = await storage.get_diagram(diagram.id)
        
        assert retrieved is not None
        assert retrieved.id == diagram.id
        assert str(retrieved.code) == sample_flowchart_code
        assert retrieved.name == "Test Diagram"

    @pytest.mark.asyncio
    async def test_delete_diagram(self, storage, sample_flowchart_code):
        """Test deleting a diagram."""
        from mermaid_view.domain.entities.diagram import Diagram
        
        diagram = Diagram.create(code=sample_flowchart_code)
        await storage.save_diagram(diagram)
        
        # Verify it exists
        assert await storage.get_diagram(diagram.id) is not None
        
        # Delete
        result = await storage.delete_diagram(diagram.id)
        
        assert result is True
        assert await storage.get_diagram(diagram.id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_diagram(self, storage):
        """Test deleting a non-existent diagram."""
        from uuid import uuid4
        
        result = await storage.delete_diagram(uuid4())
        
        assert result is False


class TestDiagramService:
    """Integration tests for DiagramService."""

    @pytest.fixture
    def mock_renderer(self):
        """Create a mock renderer."""
        renderer = MagicMock()
        renderer.is_available = AsyncMock(return_value=True)
        renderer.initialize = AsyncMock()
        renderer.cleanup = AsyncMock()
        renderer.render_to_png = AsyncMock(return_value=b'\x89PNG\r\n\x1a\n')
        renderer.render_to_svg = AsyncMock(return_value=b'<svg></svg>')
        return renderer

    @pytest.fixture
    def service(self, mock_renderer, temp_output_dir, temp_diagrams_dir):
        """Create a DiagramService with mock renderer."""
        from mermaid_view.domain.services.diagram_service import DiagramService
        
        storage = FileStorage(
            base_path=temp_output_dir.parent,
            output_dir=temp_output_dir.name,
            diagrams_dir=temp_diagrams_dir.name,
        )
        
        return DiagramService(
            renderer=mock_renderer,
            storage=storage,
        )

    @pytest.mark.asyncio
    async def test_render_diagram(self, service, sample_flowchart_code):
        """Test rendering a diagram."""
        from mermaid_view.domain.entities.diagram import Diagram
        
        diagram = Diagram.create(code=sample_flowchart_code)
        
        result = await service.render_diagram(diagram)
        
        assert isinstance(result, bytes)
        assert diagram.is_rendered()

    @pytest.mark.asyncio
    async def test_render_code(self, service, sample_flowchart_code):
        """Test rendering code directly."""
        result = await service.render_code(sample_flowchart_code)
        
        assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_render_code_and_save(self, service, sample_flowchart_code, temp_output_dir):
        """Test rendering code and saving to file."""
        output_path = temp_output_dir / "test_output.png"
        
        result = await service.render_code_and_save(
            code=sample_flowchart_code,
            output_path=output_path,
        )
        
        assert result.exists()

    @pytest.mark.asyncio
    async def test_context_manager(self, service):
        """Test service as context manager."""
        async with service:
            pass  # Just test that it doesn't raise


# Mark slow tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
