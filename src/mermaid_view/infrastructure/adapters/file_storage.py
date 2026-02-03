"""File storage adapter."""

import json
import logging
from pathlib import Path
from uuid import UUID

import aiofiles
import aiofiles.os

from mermaid_view.domain.entities.diagram import Diagram
from mermaid_view.domain.exceptions import StorageError
from mermaid_view.domain.ports.storage import IStoragePort
from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import (
    OutputFormat,
    RenderConfig,
    Theme,
)

logger = logging.getLogger(__name__)


class FileStorage(IStoragePort):
    """File system storage adapter.

    This adapter stores diagrams and rendered outputs to the local
    file system.
    """

    def __init__(
        self,
        base_path: Path | None = None,
        diagrams_dir: str = "diagrams",
        output_dir: str = "output",
    ) -> None:
        """Initialize file storage.

        Args:
            base_path: Base path for storage. Defaults to current directory.
            diagrams_dir: Subdirectory for diagram metadata.
            output_dir: Subdirectory for rendered outputs.
        """
        self._base_path = base_path or Path.cwd()
        self._diagrams_dir = self._base_path / diagrams_dir
        self._output_dir = self._base_path / output_dir

    async def save_diagram(self, diagram: Diagram) -> None:
        """Save a diagram entity to file.

        Args:
            diagram: The diagram to save.

        Raises:
            StorageError: If saving fails.
        """
        try:
            await self.ensure_directory(self._diagrams_dir)

            diagram_path = self._diagrams_dir / f"{diagram.id}.json"

            # Serialize diagram to JSON
            data = {
                "id": str(diagram.id),
                "code": str(diagram.code),
                "diagram_type": diagram.diagram_type.value,
                "name": diagram.name,
                "description": diagram.description,
                "config": {
                    "width": diagram.config.width,
                    "height": diagram.config.height,
                    "theme": diagram.config.theme.value,
                    "output_format": diagram.config.output_format.value,
                    "scale": diagram.config.scale,
                    "transparent": diagram.config.transparent,
                    "background_color": diagram.config.background_color,
                    "padding": diagram.config.padding,
                },
                "created_at": diagram.created_at.isoformat(),
                "updated_at": diagram.updated_at.isoformat(),
            }

            async with aiofiles.open(diagram_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2))

            logger.info(f"Diagram {diagram.id} saved to {diagram_path}")

        except Exception as e:
            logger.error(f"Failed to save diagram {diagram.id}: {e}")
            raise StorageError(f"Failed to save diagram: {e}") from e

    async def get_diagram(self, diagram_id: UUID) -> Diagram | None:
        """Retrieve a diagram by ID.

        Args:
            diagram_id: The diagram's unique identifier.

        Returns:
            The diagram if found, None otherwise.
        """
        diagram_path = self._diagrams_dir / f"{diagram_id}.json"

        if not await self.file_exists(diagram_path):
            return None

        try:
            async with aiofiles.open(diagram_path, "r", encoding="utf-8") as f:
                content = await f.read()

            data = json.loads(content)

            # Reconstruct diagram from JSON
            config = RenderConfig(
                width=data["config"]["width"],
                height=data["config"]["height"],
                theme=Theme(data["config"]["theme"]),
                output_format=OutputFormat(data["config"]["output_format"]),
                scale=data["config"]["scale"],
                transparent=data["config"]["transparent"],
                background_color=data["config"]["background_color"],
                padding=data["config"]["padding"],
            )

            code = MermaidCode.create(data["code"])

            from datetime import datetime

            diagram = Diagram(
                id=UUID(data["id"]),
                code=code,
                config=config,
                name=data.get("name"),
                description=data.get("description"),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )

            return diagram

        except Exception as e:
            logger.error(f"Failed to load diagram {diagram_id}: {e}")
            return None

    async def delete_diagram(self, diagram_id: UUID) -> bool:
        """Delete a diagram.

        Args:
            diagram_id: The diagram's unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        diagram_path = self._diagrams_dir / f"{diagram_id}.json"

        if not await self.file_exists(diagram_path):
            return False

        try:
            await aiofiles.os.remove(diagram_path)
            logger.info(f"Diagram {diagram_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete diagram {diagram_id}: {e}")
            raise StorageError(f"Failed to delete diagram: {e}") from e

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
        try:
            # Make path absolute if relative
            if not output_path.is_absolute():
                output_path = self._output_dir / output_path

            # Ensure parent directory exists
            await self.ensure_directory(output_path.parent)

            # Write file
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(data)

            logger.info(f"Rendered output saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to save rendered output: {e}")
            raise StorageError(f"Failed to save rendered output: {e}") from e

    async def read_file(self, file_path: Path) -> bytes:
        """Read a file's contents.

        Args:
            file_path: The path to read from.

        Returns:
            The file contents as bytes.

        Raises:
            StorageError: If reading fails.
        """
        try:
            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()
        except FileNotFoundError:
            raise StorageError(f"File not found: {file_path}")
        except Exception as e:
            raise StorageError(f"Failed to read file: {e}") from e

    async def file_exists(self, file_path: Path) -> bool:
        """Check if a file exists.

        Args:
            file_path: The path to check.

        Returns:
            True if the file exists.
        """
        try:
            return await aiofiles.os.path.exists(file_path)
        except Exception:
            return False

    async def ensure_directory(self, directory: Path) -> None:
        """Ensure a directory exists, creating it if necessary.

        Args:
            directory: The directory path.

        Raises:
            StorageError: If creation fails.
        """
        try:
            if not await aiofiles.os.path.exists(directory):
                await aiofiles.os.makedirs(directory, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
        except Exception as e:
            raise StorageError(f"Failed to create directory: {e}") from e

    @property
    def output_directory(self) -> Path:
        """Get the output directory path.

        Returns:
            The output directory path.
        """
        return self._output_dir

    @property
    def diagrams_directory(self) -> Path:
        """Get the diagrams directory path.

        Returns:
            The diagrams directory path.
        """
        return self._diagrams_dir
