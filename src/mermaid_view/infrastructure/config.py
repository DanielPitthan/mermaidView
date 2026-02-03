"""Application configuration."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration settings."""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Renderer settings
    renderer_timeout: int = 30000  # milliseconds
    headless: bool = True
    use_fallback: bool = True

    # Storage settings
    output_dir: Path = field(default_factory=lambda: Path("output"))
    diagrams_dir: Path = field(default_factory=lambda: Path("diagrams"))

    # Mermaid settings
    default_theme: str = "default"
    default_width: int = 800
    default_height: int = 600
    default_scale: float = 2.0

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables.

        Returns:
            AppConfig instance with values from environment.
        """
        return cls(
            host=os.getenv("MERMAID_VIEW_HOST", "0.0.0.0"),
            port=int(os.getenv("MERMAID_VIEW_PORT", "8000")),
            debug=os.getenv("MERMAID_VIEW_DEBUG", "false").lower() == "true",
            renderer_timeout=int(os.getenv("MERMAID_VIEW_TIMEOUT", "30000")),
            headless=os.getenv("MERMAID_VIEW_HEADLESS", "true").lower() == "true",
            use_fallback=os.getenv("MERMAID_VIEW_USE_FALLBACK", "true").lower() == "true",
            output_dir=Path(os.getenv("MERMAID_VIEW_OUTPUT_DIR", "output")),
            diagrams_dir=Path(os.getenv("MERMAID_VIEW_DIAGRAMS_DIR", "diagrams")),
            default_theme=os.getenv("MERMAID_VIEW_THEME", "default"),
            default_width=int(os.getenv("MERMAID_VIEW_WIDTH", "800")),
            default_height=int(os.getenv("MERMAID_VIEW_HEIGHT", "600")),
            default_scale=float(os.getenv("MERMAID_VIEW_SCALE", "2.0")),
        )


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance.

    Returns:
        The application configuration.
    """
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance.

    Args:
        config: The configuration to set.
    """
    global _config
    _config = config
