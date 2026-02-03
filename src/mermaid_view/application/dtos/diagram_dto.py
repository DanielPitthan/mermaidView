"""Data Transfer Objects for diagrams."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from mermaid_view.domain.value_objects.render_config import OutputFormat, Theme


class RenderRequestDTO(BaseModel):
    """DTO for diagram render requests."""

    code: str = Field(..., description="Mermaid diagram code", min_length=1)
    output_path: Optional[str] = Field(
        None, description="Output file path (optional for web API)"
    )
    width: int = Field(default=800, ge=100, le=4000, description="Output width")
    height: int = Field(default=600, ge=100, le=4000, description="Output height")
    theme: Theme = Field(default=Theme.DEFAULT, description="Mermaid theme")
    output_format: OutputFormat = Field(
        default=OutputFormat.PNG, description="Output format"
    )
    scale: float = Field(default=2.0, ge=0.5, le=4.0, description="Scale factor")
    transparent: bool = Field(default=False, description="Transparent background")
    background_color: str = Field(default="white", description="Background color")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate that code is not empty."""
        if not v or not v.strip():
            raise ValueError("Mermaid code cannot be empty")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "graph TD\n    A[Start] --> B[End]",
                    "output_path": "output.png",
                    "width": 800,
                    "height": 600,
                    "theme": "default",
                    "output_format": "png",
                }
            ]
        }
    }


class RenderResponseDTO(BaseModel):
    """DTO for diagram render responses."""

    success: bool = Field(..., description="Whether rendering succeeded")
    diagram_id: Optional[UUID] = Field(None, description="ID of the rendered diagram")
    output_path: Optional[str] = Field(None, description="Path to the output file")
    message: str = Field(default="", description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")
    data_base64: Optional[str] = Field(
        None, description="Base64 encoded image data (for web API)"
    )
    content_type: str = Field(default="image/png", description="MIME type of output")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "diagram_id": "123e4567-e89b-12d3-a456-426614174000",
                    "output_path": "output.png",
                    "message": "Diagram rendered successfully",
                }
            ]
        }
    }


class DiagramDTO(BaseModel):
    """DTO for diagram entity."""

    id: UUID = Field(..., description="Diagram unique identifier")
    code: str = Field(..., description="Mermaid diagram code")
    diagram_type: str = Field(..., description="Type of diagram")
    name: Optional[str] = Field(None, description="Diagram name")
    description: Optional[str] = Field(None, description="Diagram description")
    width: int = Field(..., description="Configured width")
    height: int = Field(..., description="Configured height")
    theme: str = Field(..., description="Mermaid theme")
    output_format: str = Field(..., description="Output format")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_rendered: bool = Field(..., description="Whether diagram has been rendered")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "code": "graph TD\n    A --> B",
                    "diagram_type": "flowchart",
                    "name": "My Diagram",
                    "width": 800,
                    "height": 600,
                    "theme": "default",
                    "output_format": "png",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "is_rendered": False,
                }
            ]
        }
    }

    @classmethod
    def from_entity(cls, diagram) -> "DiagramDTO":
        """Create DTO from Diagram entity.

        Args:
            diagram: The Diagram entity.

        Returns:
            A DiagramDTO instance.
        """
        return cls(
            id=diagram.id,
            code=str(diagram.code),
            diagram_type=diagram.diagram_type.value,
            name=diagram.name,
            description=diagram.description,
            width=diagram.config.width,
            height=diagram.config.height,
            theme=diagram.config.theme.value,
            output_format=diagram.config.output_format.value,
            created_at=diagram.created_at,
            updated_at=diagram.updated_at,
            is_rendered=diagram.is_rendered(),
        )


class HealthDTO(BaseModel):
    """DTO for health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    renderer_available: bool = Field(..., description="Whether renderer is available")
