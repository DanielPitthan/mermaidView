"""Render configuration value object."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Self


class OutputFormat(str, Enum):
    """Supported output formats."""

    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


class Theme(str, Enum):
    """Mermaid theme options."""

    DEFAULT = "default"
    FOREST = "forest"
    DARK = "dark"
    NEUTRAL = "neutral"
    BASE = "base"


@dataclass(frozen=True)
class RenderConfig:
    """Value object for diagram rendering configuration.

    This is an immutable configuration object that specifies
    how a Mermaid diagram should be rendered.
    """

    width: int = 800
    height: int = 600
    background_color: str = "white"
    theme: Theme = Theme.DEFAULT
    output_format: OutputFormat = OutputFormat.PNG
    scale: float = 1.0
    transparent: bool = False
    padding: int = 20

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.width <= 0:
            raise ValueError("Width must be positive")
        if self.height <= 0:
            raise ValueError("Height must be positive")
        if self.scale <= 0:
            raise ValueError("Scale must be positive")
        if self.padding < 0:
            raise ValueError("Padding cannot be negative")

    @classmethod
    def default(cls) -> Self:
        """Create a default render configuration.

        Returns:
            A new RenderConfig with default settings.
        """
        return cls()

    @classmethod
    def for_png(
        cls,
        width: int = 800,
        height: int = 600,
        theme: Theme = Theme.DEFAULT,
        scale: float = 2.0,
        transparent: bool = False,
    ) -> Self:
        """Create a configuration optimized for PNG output.

        Args:
            width: Image width in pixels.
            height: Image height in pixels.
            theme: Mermaid theme to use.
            scale: Scale factor for higher resolution.
            transparent: Whether background should be transparent.

        Returns:
            A new RenderConfig for PNG output.
        """
        return cls(
            width=width,
            height=height,
            theme=theme,
            output_format=OutputFormat.PNG,
            scale=scale,
            transparent=transparent,
            background_color="transparent" if transparent else "white",
        )

    @classmethod
    def for_svg(cls, theme: Theme = Theme.DEFAULT) -> Self:
        """Create a configuration for SVG output.

        Args:
            theme: Mermaid theme to use.

        Returns:
            A new RenderConfig for SVG output.
        """
        return cls(
            theme=theme,
            output_format=OutputFormat.SVG,
        )

    def with_size(self, width: int, height: int) -> Self:
        """Create a new config with different size.

        Args:
            width: New width.
            height: New height.

        Returns:
            A new RenderConfig with updated size.
        """
        return RenderConfig(
            width=width,
            height=height,
            background_color=self.background_color,
            theme=self.theme,
            output_format=self.output_format,
            scale=self.scale,
            transparent=self.transparent,
            padding=self.padding,
        )

    def with_theme(self, theme: Theme) -> Self:
        """Create a new config with different theme.

        Args:
            theme: New theme.

        Returns:
            A new RenderConfig with updated theme.
        """
        return RenderConfig(
            width=self.width,
            height=self.height,
            background_color=self.background_color,
            theme=theme,
            output_format=self.output_format,
            scale=self.scale,
            transparent=self.transparent,
            padding=self.padding,
        )

    def to_mermaid_config(self) -> dict:
        """Convert to Mermaid.js configuration format.

        Returns:
            A dictionary with Mermaid.js configuration.
        """
        return {
            "theme": self.theme.value,
            "startOnLoad": True,
            "securityLevel": "loose",
            "flowchart": {
                "useMaxWidth": True,
                "htmlLabels": True,
            },
        }
