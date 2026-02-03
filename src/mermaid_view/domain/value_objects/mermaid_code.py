"""Mermaid code value object."""

from dataclasses import dataclass
from typing import Self

from mermaid_view.domain.exceptions import InvalidMermaidCodeError
from mermaid_view.domain.value_objects.diagram_type import DiagramType


@dataclass(frozen=True)
class MermaidCode:
    """Value object representing Mermaid diagram code.

    This is an immutable value object that encapsulates the Mermaid
    diagram code and provides validation.
    """

    value: str
    diagram_type: DiagramType

    def __post_init__(self) -> None:
        """Validate the Mermaid code after initialization."""
        if not self.value or not self.value.strip():
            raise InvalidMermaidCodeError("Mermaid code cannot be empty")

    @classmethod
    def create(cls, code: str) -> Self:
        """Create a MermaidCode instance from raw code string.

        Args:
            code: The raw Mermaid code string.

        Returns:
            A new MermaidCode instance.

        Raises:
            InvalidMermaidCodeError: If the code is invalid.
        """
        if not code or not code.strip():
            raise InvalidMermaidCodeError("Mermaid code cannot be empty")

        normalized_code = code.strip()
        diagram_type = DiagramType.detect_from_code(normalized_code)

        return cls(value=normalized_code, diagram_type=diagram_type)

    def __str__(self) -> str:
        """Return the string representation of the Mermaid code."""
        return self.value

    def __len__(self) -> int:
        """Return the length of the Mermaid code."""
        return len(self.value)

    def get_lines(self) -> list[str]:
        """Split the code into lines.

        Returns:
            A list of code lines.
        """
        return self.value.splitlines()

    def is_valid_syntax(self) -> bool:
        """Check if the code has valid basic syntax.

        This performs basic validation. Full validation is done
        during rendering by Mermaid.js.

        Returns:
            True if basic syntax appears valid.
        """
        # Basic validation - check if code starts with a known diagram type
        return self.diagram_type != DiagramType.UNKNOWN
