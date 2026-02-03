"""Render diagram command."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from mermaid_view.domain.value_objects.render_config import OutputFormat, Theme


@dataclass(frozen=True)
class RenderDiagramCommand:
    """Command to render a Mermaid diagram.

    This command encapsulates all the information needed to
    render a diagram to an output format.
    """

    code: str
    output_path: Optional[Path] = None
    width: int = 800
    height: int = 600
    theme: Theme = Theme.DEFAULT
    output_format: OutputFormat = OutputFormat.PNG
    scale: float = 2.0
    transparent: bool = False
    background_color: str = "white"
    name: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate command after initialization."""
        if not self.code or not self.code.strip():
            raise ValueError("Code cannot be empty")
        if self.width <= 0:
            raise ValueError("Width must be positive")
        if self.height <= 0:
            raise ValueError("Height must be positive")
        if self.scale <= 0:
            raise ValueError("Scale must be positive")

    @classmethod
    def from_dto(cls, dto) -> "RenderDiagramCommand":
        """Create command from RenderRequestDTO.

        Args:
            dto: The request DTO.

        Returns:
            A RenderDiagramCommand instance.
        """
        return cls(
            code=dto.code,
            output_path=Path(dto.output_path) if dto.output_path else None,
            width=dto.width,
            height=dto.height,
            theme=dto.theme,
            output_format=dto.output_format,
            scale=dto.scale,
            transparent=dto.transparent,
            background_color=dto.background_color,
        )
