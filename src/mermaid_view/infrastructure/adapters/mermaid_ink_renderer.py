"""Mermaid.ink API renderer adapter."""

import base64
import logging
import zlib
from typing import Optional

import httpx

from mermaid_view.domain.exceptions import NetworkError, RenderError
from mermaid_view.domain.ports.renderer import IRenderPort
from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import OutputFormat, RenderConfig

logger = logging.getLogger(__name__)

# Mermaid.ink API base URL
MERMAID_INK_BASE_URL = "https://mermaid.ink"


class MermaidInkRenderer(IRenderPort):
    """Renderer that uses the mermaid.ink API to render diagrams.

    This adapter sends Mermaid code to the mermaid.ink service
    and receives the rendered image. Useful as a fallback when
    Playwright is not available.
    """

    def __init__(
        self,
        base_url: str = MERMAID_INK_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the Mermaid.ink renderer.

        Args:
            base_url: The mermaid.ink API base URL.
            timeout: HTTP request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the HTTP client."""
        if self._initialized:
            return

        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
        )
        self._initialized = True
        logger.info("Mermaid.ink renderer initialized")

    async def cleanup(self) -> None:
        """Cleanup HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._initialized = False
        logger.info("Mermaid.ink renderer cleaned up")

    async def is_available(self) -> bool:
        """Check if mermaid.ink service is available.

        Returns:
            True if the service can be reached.
        """
        try:
            if not self._initialized:
                await self.initialize()

            response = await self._client.head(self._base_url)
            return response.status_code < 500
        except Exception:
            return False

    async def render_to_png(self, code: MermaidCode, config: RenderConfig) -> bytes:
        """Render Mermaid code to PNG format using mermaid.ink.

        Args:
            code: The Mermaid code to render.
            config: Rendering configuration.

        Returns:
            PNG image data as bytes.

        Raises:
            RenderError: If rendering fails.
        """
        if not self._initialized:
            await self.initialize()

        encoded = self._encode_diagram(str(code))
        url = f"{self._base_url}/img/pako:{encoded}"

        # Add query parameters for configuration
        params = self._build_params(config, OutputFormat.PNG)
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())

        return await self._fetch_image(url)

    async def render_to_svg(self, code: MermaidCode, config: RenderConfig) -> bytes:
        """Render Mermaid code to SVG format using mermaid.ink.

        Args:
            code: The Mermaid code to render.
            config: Rendering configuration.

        Returns:
            SVG data as bytes.

        Raises:
            RenderError: If rendering fails.
        """
        if not self._initialized:
            await self.initialize()

        encoded = self._encode_diagram(str(code))
        url = f"{self._base_url}/svg/pako:{encoded}"

        # Add query parameters for configuration
        params = self._build_params(config, OutputFormat.SVG)
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())

        return await self._fetch_image(url)

    async def _fetch_image(self, url: str) -> bytes:
        """Fetch image from URL.

        Args:
            url: The image URL.

        Returns:
            Image data as bytes.

        Raises:
            RenderError: If fetching fails.
        """
        try:
            response = await self._client.get(url)

            if response.status_code != 200:
                error_text = response.text[:500] if response.text else "Unknown error"
                raise RenderError(
                    f"Mermaid.ink returned status {response.status_code}: {error_text}"
                )

            return response.content

        except httpx.TimeoutException as e:
            raise RenderError(f"Request to mermaid.ink timed out: {e}") from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error connecting to mermaid.ink: {e}") from e
        except RenderError:
            raise
        except Exception as e:
            raise RenderError(f"Failed to fetch image from mermaid.ink: {e}") from e

    def _encode_diagram(self, code: str) -> str:
        """Encode diagram code for mermaid.ink URL.

        Uses pako (zlib) compression and base64 URL-safe encoding.

        Args:
            code: The Mermaid code.

        Returns:
            Encoded string for URL.
        """
        # Compress using zlib (pako compatible)
        compressed = zlib.compress(code.encode("utf-8"), level=9)

        # Base64 URL-safe encoding
        encoded = base64.urlsafe_b64encode(compressed).decode("ascii")

        # Remove padding
        encoded = encoded.rstrip("=")

        return encoded

    def _build_params(
        self, config: RenderConfig, output_format: OutputFormat
    ) -> dict[str, str]:
        """Build query parameters for mermaid.ink request.

        Args:
            config: Render configuration.
            output_format: Output format.

        Returns:
            Dictionary of query parameters.
        """
        params = {}

        # Theme
        if config.theme.value != "default":
            params["theme"] = config.theme.value

        # Background color (for PNG)
        if output_format == OutputFormat.PNG and config.background_color != "white":
            params["bgColor"] = config.background_color

        # Scale
        if config.scale != 1.0:
            params["scale"] = str(config.scale)

        # Width
        if config.width != 800:
            params["width"] = str(config.width)

        # Height  
        if config.height != 600:
            params["height"] = str(config.height)

        return params
