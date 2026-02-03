"""Diagram entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from mermaid_view.domain.value_objects.diagram_type import DiagramType
from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import RenderConfig


@dataclass
class Diagram:
    """Domain entity representing a Mermaid diagram.

    This entity encapsulates the diagram code, type, rendering
    configuration, and metadata.
    """

    id: UUID
    code: MermaidCode
    config: RenderConfig
    created_at: datetime
    updated_at: datetime
    name: str | None = None
    description: str | None = None
    rendered_data: bytes | None = field(default=None, repr=False)

    @classmethod
    def create(
        cls,
        code: str | MermaidCode,
        config: RenderConfig | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> Self:
        """Create a new Diagram entity.

        Args:
            code: The Mermaid code (string or MermaidCode object).
            config: Optional render configuration.
            name: Optional diagram name.
            description: Optional description.

        Returns:
            A new Diagram entity.
        """
        if isinstance(code, str):
            mermaid_code = MermaidCode.create(code)
        else:
            mermaid_code = code

        now = datetime.utcnow()

        return cls(
            id=uuid4(),
            code=mermaid_code,
            config=config or RenderConfig.default(),
            created_at=now,
            updated_at=now,
            name=name,
            description=description,
        )

    @property
    def diagram_type(self) -> DiagramType:
        """Get the diagram type.

        Returns:
            The type of diagram.
        """
        return self.code.diagram_type

    def update_code(self, new_code: str | MermaidCode) -> None:
        """Update the diagram code.

        Args:
            new_code: The new Mermaid code.
        """
        if isinstance(new_code, str):
            self.code = MermaidCode.create(new_code)
        else:
            self.code = new_code
        self.updated_at = datetime.utcnow()
        self.rendered_data = None  # Clear cached render

    def update_config(self, new_config: RenderConfig) -> None:
        """Update the render configuration.

        Args:
            new_config: The new configuration.
        """
        self.config = new_config
        self.updated_at = datetime.utcnow()
        self.rendered_data = None  # Clear cached render

    def set_rendered_data(self, data: bytes) -> None:
        """Set the rendered diagram data.

        Args:
            data: The rendered image data.
        """
        self.rendered_data = data
        self.updated_at = datetime.utcnow()

    def is_rendered(self) -> bool:
        """Check if the diagram has been rendered.

        Returns:
            True if rendered data exists.
        """
        return self.rendered_data is not None

    def get_code_string(self) -> str:
        """Get the diagram code as a string.

        Returns:
            The Mermaid code string.
        """
        return str(self.code)

    def __str__(self) -> str:
        """Return string representation."""
        return f"Diagram({self.id}, type={self.diagram_type.value})"

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"Diagram(id={self.id}, "
            f"type={self.diagram_type.value}, "
            f"name={self.name!r}, "
            f"created_at={self.created_at})"
        )
