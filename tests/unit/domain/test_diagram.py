"""Unit tests for domain layer."""

import pytest
from uuid import UUID
from datetime import datetime

from mermaid_view.domain.entities.diagram import Diagram
from mermaid_view.domain.value_objects.diagram_type import DiagramType
from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import (
    RenderConfig,
    OutputFormat,
    Theme,
)
from mermaid_view.domain.exceptions import InvalidMermaidCodeError


class TestDiagramType:
    """Tests for DiagramType enum."""

    def test_detect_flowchart(self):
        """Test detection of flowchart diagram."""
        assert DiagramType.detect_from_code("graph TD; A-->B") == DiagramType.FLOWCHART
        assert DiagramType.detect_from_code("flowchart LR; A-->B") == DiagramType.FLOWCHART

    def test_detect_sequence(self):
        """Test detection of sequence diagram."""
        assert DiagramType.detect_from_code("sequenceDiagram\nAlice->>Bob: Hi") == DiagramType.SEQUENCE

    def test_detect_class(self):
        """Test detection of class diagram."""
        assert DiagramType.detect_from_code("classDiagram\nAnimal <|-- Duck") == DiagramType.CLASS

    def test_detect_state(self):
        """Test detection of state diagram."""
        assert DiagramType.detect_from_code("stateDiagram-v2\n[*] --> Still") == DiagramType.STATE

    def test_detect_er(self):
        """Test detection of ER diagram."""
        assert DiagramType.detect_from_code("erDiagram\nCUSTOMER ||--o{ ORDER") == DiagramType.ER

    def test_detect_gantt(self):
        """Test detection of Gantt diagram."""
        assert DiagramType.detect_from_code("gantt\ntitle Project") == DiagramType.GANTT

    def test_detect_pie(self):
        """Test detection of pie chart."""
        assert DiagramType.detect_from_code("pie\ntitle Pets") == DiagramType.PIE

    def test_detect_unknown(self):
        """Test detection of unknown diagram type."""
        assert DiagramType.detect_from_code("unknown content") == DiagramType.UNKNOWN

    def test_detect_with_whitespace(self):
        """Test detection with leading whitespace."""
        assert DiagramType.detect_from_code("  graph TD; A-->B") == DiagramType.FLOWCHART


class TestMermaidCode:
    """Tests for MermaidCode value object."""

    def test_create_valid_code(self):
        """Test creating MermaidCode with valid input."""
        code = MermaidCode.create("graph TD; A-->B")
        assert str(code) == "graph TD; A-->B"
        assert code.diagram_type == DiagramType.FLOWCHART

    def test_create_empty_code_raises_error(self):
        """Test that empty code raises InvalidMermaidCodeError."""
        with pytest.raises(InvalidMermaidCodeError):
            MermaidCode.create("")

    def test_create_whitespace_only_raises_error(self):
        """Test that whitespace-only code raises InvalidMermaidCodeError."""
        with pytest.raises(InvalidMermaidCodeError):
            MermaidCode.create("   \n\t  ")

    def test_code_is_immutable(self):
        """Test that MermaidCode is immutable (frozen)."""
        code = MermaidCode.create("graph TD; A-->B")
        with pytest.raises(AttributeError):
            code.value = "new value"

    def test_get_lines(self):
        """Test get_lines method."""
        code = MermaidCode.create("graph TD\nA-->B\nB-->C")
        lines = code.get_lines()
        assert len(lines) == 3
        assert lines[0] == "graph TD"
        assert lines[1] == "A-->B"

    def test_len(self):
        """Test __len__ method."""
        code = MermaidCode.create("graph TD; A-->B")
        assert len(code) == 15

    def test_is_valid_syntax_known_type(self):
        """Test is_valid_syntax for known diagram type."""
        code = MermaidCode.create("graph TD; A-->B")
        assert code.is_valid_syntax() is True

    def test_is_valid_syntax_unknown_type(self):
        """Test is_valid_syntax for unknown diagram type."""
        code = MermaidCode.create("unknown content")
        assert code.is_valid_syntax() is False


class TestRenderConfig:
    """Tests for RenderConfig value object."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RenderConfig.default()
        assert config.width == 800
        assert config.height == 600
        assert config.theme == Theme.DEFAULT
        assert config.output_format == OutputFormat.PNG
        assert config.scale == 1.0
        assert config.transparent is False

    def test_for_png_config(self):
        """Test PNG-optimized configuration."""
        config = RenderConfig.for_png(width=1200, height=800, scale=2.0)
        assert config.width == 1200
        assert config.height == 800
        assert config.output_format == OutputFormat.PNG
        assert config.scale == 2.0

    def test_for_svg_config(self):
        """Test SVG configuration."""
        config = RenderConfig.for_svg(theme=Theme.DARK)
        assert config.output_format == OutputFormat.SVG
        assert config.theme == Theme.DARK

    def test_with_size(self):
        """Test with_size method."""
        config = RenderConfig.default()
        new_config = config.with_size(1000, 800)
        assert new_config.width == 1000
        assert new_config.height == 800
        assert new_config.theme == config.theme  # Unchanged

    def test_with_theme(self):
        """Test with_theme method."""
        config = RenderConfig.default()
        new_config = config.with_theme(Theme.FOREST)
        assert new_config.theme == Theme.FOREST
        assert new_config.width == config.width  # Unchanged

    def test_invalid_width_raises_error(self):
        """Test that invalid width raises ValueError."""
        with pytest.raises(ValueError):
            RenderConfig(width=0)

    def test_invalid_height_raises_error(self):
        """Test that invalid height raises ValueError."""
        with pytest.raises(ValueError):
            RenderConfig(height=-100)

    def test_invalid_scale_raises_error(self):
        """Test that invalid scale raises ValueError."""
        with pytest.raises(ValueError):
            RenderConfig(scale=0)

    def test_to_mermaid_config(self):
        """Test conversion to Mermaid.js config format."""
        config = RenderConfig(theme=Theme.DARK)
        mermaid_config = config.to_mermaid_config()
        assert mermaid_config["theme"] == "dark"
        assert mermaid_config["startOnLoad"] is True


class TestDiagram:
    """Tests for Diagram entity."""

    def test_create_diagram(self):
        """Test creating a diagram entity."""
        diagram = Diagram.create(code="graph TD; A-->B", name="Test Diagram")
        
        assert isinstance(diagram.id, UUID)
        assert str(diagram.code) == "graph TD; A-->B"
        assert diagram.diagram_type == DiagramType.FLOWCHART
        assert diagram.name == "Test Diagram"
        assert isinstance(diagram.created_at, datetime)
        assert diagram.is_rendered() is False

    def test_create_with_mermaid_code_object(self):
        """Test creating diagram with MermaidCode object."""
        mermaid_code = MermaidCode.create("sequenceDiagram\nAlice->>Bob: Hi")
        diagram = Diagram.create(code=mermaid_code)
        
        assert diagram.diagram_type == DiagramType.SEQUENCE

    def test_update_code(self):
        """Test updating diagram code."""
        diagram = Diagram.create(code="graph TD; A-->B")
        old_updated_at = diagram.updated_at
        
        diagram.update_code("sequenceDiagram\nAlice->>Bob: Hi")
        
        assert diagram.diagram_type == DiagramType.SEQUENCE
        assert diagram.updated_at >= old_updated_at

    def test_update_config(self):
        """Test updating diagram config."""
        diagram = Diagram.create(code="graph TD; A-->B")
        new_config = RenderConfig.for_png(width=1200, height=800)
        
        diagram.update_config(new_config)
        
        assert diagram.config.width == 1200
        assert diagram.config.height == 800

    def test_set_rendered_data(self):
        """Test setting rendered data."""
        diagram = Diagram.create(code="graph TD; A-->B")
        assert diagram.is_rendered() is False
        
        diagram.set_rendered_data(b"PNG data here")
        
        assert diagram.is_rendered() is True
        assert diagram.rendered_data == b"PNG data here"

    def test_get_code_string(self):
        """Test get_code_string method."""
        diagram = Diagram.create(code="graph TD; A-->B")
        assert diagram.get_code_string() == "graph TD; A-->B"

    def test_str_representation(self):
        """Test string representation."""
        diagram = Diagram.create(code="graph TD; A-->B")
        str_repr = str(diagram)
        assert "Diagram" in str_repr
        assert "flowchart" in str_repr


class TestTheme:
    """Tests for Theme enum."""

    def test_all_themes_exist(self):
        """Test that all expected themes exist."""
        expected_themes = ["default", "forest", "dark", "neutral", "base"]
        for theme_name in expected_themes:
            assert hasattr(Theme, theme_name.upper())

    def test_theme_values(self):
        """Test theme values are correct strings."""
        assert Theme.DEFAULT.value == "default"
        assert Theme.DARK.value == "dark"
        assert Theme.FOREST.value == "forest"


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_all_formats_exist(self):
        """Test that all expected formats exist."""
        assert OutputFormat.PNG.value == "png"
        assert OutputFormat.SVG.value == "svg"
        assert OutputFormat.PDF.value == "pdf"
