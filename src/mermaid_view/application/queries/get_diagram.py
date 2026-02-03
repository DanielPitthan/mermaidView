"""Get diagram query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetDiagramQuery:
    """Query to retrieve a diagram by ID.

    This query encapsulates the request to fetch a diagram.
    """

    diagram_id: UUID

    @classmethod
    def from_string(cls, diagram_id: str) -> "GetDiagramQuery":
        """Create query from string ID.

        Args:
            diagram_id: The diagram ID as a string.

        Returns:
            A GetDiagramQuery instance.

        Raises:
            ValueError: If the ID is invalid.
        """
        return cls(diagram_id=UUID(diagram_id))
