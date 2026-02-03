"""Storage port interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID

from mermaid_view.domain.entities.diagram import Diagram


class IStoragePort(ABC):
    """Interface for diagram storage adapters.

    This port defines the contract for storing and retrieving
    diagrams and their rendered outputs.
    """

    @abstractmethod
    async def save_diagram(self, diagram: Diagram) -> None:
        """Save a diagram entity.

        Args:
            diagram: The diagram to save.

        Raises:
            StorageError: If saving fails.
        """
        pass

    @abstractmethod
    async def get_diagram(self, diagram_id: UUID) -> Diagram | None:
        """Retrieve a diagram by ID.

        Args:
            diagram_id: The diagram's unique identifier.

        Returns:
            The diagram if found, None otherwise.
        """
        pass

    @abstractmethod
    async def delete_diagram(self, diagram_id: UUID) -> bool:
        """Delete a diagram.

        Args:
            diagram_id: The diagram's unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def save_rendered_output(
        self,
        data: bytes,
        output_path: Path,
    ) -> Path:
        """Save rendered diagram output to file.

        Args:
            data: The rendered image data.
            output_path: The path to save to.

        Returns:
            The actual path where the file was saved.

        Raises:
            StorageError: If saving fails.
        """
        pass

    @abstractmethod
    async def read_file(self, file_path: Path) -> bytes:
        """Read a file's contents.

        Args:
            file_path: The path to read from.

        Returns:
            The file contents as bytes.

        Raises:
            StorageError: If reading fails.
        """
        pass

    @abstractmethod
    async def file_exists(self, file_path: Path) -> bool:
        """Check if a file exists.

        Args:
            file_path: The path to check.

        Returns:
            True if the file exists.
        """
        pass

    @abstractmethod
    async def ensure_directory(self, directory: Path) -> None:
        """Ensure a directory exists, creating it if necessary.

        Args:
            directory: The directory path.

        Raises:
            StorageError: If creation fails.
        """
        pass
