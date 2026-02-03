"""Playwright-based Mermaid renderer adapter."""

import asyncio
import json
import logging
from typing import Optional

from mermaid_view.domain.exceptions import BrowserError, RenderError
from mermaid_view.domain.ports.renderer import IRenderPort
from mermaid_view.domain.value_objects.mermaid_code import MermaidCode
from mermaid_view.domain.value_objects.render_config import RenderConfig

logger = logging.getLogger(__name__)

# Mermaid CDN URL - using version 11.12.2 as specified in requirements
MERMAID_CDN_URL = "https://cdn.jsdelivr.net/npm/mermaid@11.12.2/dist/mermaid.esm.min.mjs"


class PlaywrightRenderer(IRenderPort):
    """Renderer that uses Playwright to render Mermaid diagrams.

    This adapter creates a headless browser, loads Mermaid.js via CDN,
    renders the diagram, and captures the output as PNG or SVG.
    """

    def __init__(
        self,
        timeout: int = 30000,
        headless: bool = True,
    ) -> None:
        """Initialize the Playwright renderer.

        Args:
            timeout: Timeout in milliseconds for rendering.
            headless: Whether to run browser in headless mode.
        """
        self._timeout = timeout
        self._headless = headless
        self._browser = None
        self._playwright = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Playwright and launch browser."""
        if self._initialized:
            return

        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self._headless,
            )
            self._initialized = True
            logger.info("Playwright renderer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
            raise BrowserError(f"Failed to initialize browser: {e}") from e

    async def cleanup(self) -> None:
        """Cleanup Playwright resources."""
        if self._browser:
            try:
                await self._browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping Playwright: {e}")
            self._playwright = None

        self._initialized = False
        logger.info("Playwright renderer cleaned up")

    async def is_available(self) -> bool:
        """Check if Playwright is available.

        Returns:
            True if Playwright can be used.
        """
        try:
            from playwright.async_api import async_playwright

            return True
        except ImportError:
            return False

    async def render_to_png(self, code: MermaidCode, config: RenderConfig) -> bytes:
        """Render Mermaid code to PNG format.

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

        html_content = self._generate_html(code, config)

        try:
            page = await self._browser.new_page()

            # Set viewport size
            await page.set_viewport_size({
                "width": config.width,
                "height": config.height,
            })

            # Load HTML content
            await page.set_content(html_content, wait_until="networkidle")

            # Wait for Mermaid to render
            await self._wait_for_render(page)

            # Get the SVG element
            svg_element = await page.query_selector(".mermaid svg")
            if not svg_element:
                raise RenderError("Failed to render diagram: SVG not found")

            # Get bounding box for proper sizing
            bounding_box = await svg_element.bounding_box()

            if bounding_box:
                # Take screenshot of the SVG element
                screenshot = await svg_element.screenshot(
                    type="png",
                    scale="device" if config.scale == 1.0 else "css",
                    omit_background=config.transparent,
                )
            else:
                # Fallback to full page screenshot
                screenshot = await page.screenshot(
                    type="png",
                    full_page=False,
                    omit_background=config.transparent,
                )

            await page.close()
            return screenshot

        except Exception as e:
            logger.error(f"Render to PNG failed: {e}")
            raise RenderError(f"Failed to render diagram to PNG: {e}") from e

    async def render_to_svg(self, code: MermaidCode, config: RenderConfig) -> bytes:
        """Render Mermaid code to SVG format.

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

        html_content = self._generate_html(code, config)

        try:
            page = await self._browser.new_page()

            # Set viewport size
            await page.set_viewport_size({
                "width": config.width,
                "height": config.height,
            })

            # Load HTML content
            await page.set_content(html_content, wait_until="networkidle")

            # Wait for Mermaid to render
            await self._wait_for_render(page)

            # Extract SVG content
            svg_content = await page.evaluate("""
                () => {
                    const svg = document.querySelector('.mermaid svg');
                    if (!svg) return null;
                    return svg.outerHTML;
                }
            """)

            await page.close()

            if not svg_content:
                raise RenderError("Failed to render diagram: SVG not found")

            return svg_content.encode("utf-8")

        except Exception as e:
            logger.error(f"Render to SVG failed: {e}")
            raise RenderError(f"Failed to render diagram to SVG: {e}") from e

    async def _wait_for_render(self, page, timeout: int = 10000) -> None:
        """Wait for Mermaid to complete rendering.

        Args:
            page: The Playwright page.
            timeout: Timeout in milliseconds.
        """
        try:
            # Wait for the SVG to appear
            await page.wait_for_selector(".mermaid svg", timeout=timeout)

            # Additional wait for animations/transitions
            await page.wait_for_timeout(500)

        except Exception as e:
            raise RenderError(f"Timeout waiting for diagram render: {e}") from e

    def _generate_html(self, code: MermaidCode, config: RenderConfig) -> str:
        """Generate HTML page with Mermaid diagram.

        Args:
            code: The Mermaid code.
            config: Rendering configuration.

        Returns:
            HTML content as string.
        """
        mermaid_config = json.dumps(config.to_mermaid_config())
        escaped_code = self._escape_html(str(code))

        background = "transparent" if config.transparent else config.background_color

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background-color: {background};
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            padding: {config.padding}px;
        }}
        .mermaid {{
            background-color: {background};
        }}
        .mermaid svg {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{escaped_code}
    </div>
    <script type="module">
        import mermaid from '{MERMAID_CDN_URL}';
        mermaid.initialize({mermaid_config});
        await mermaid.run();
    </script>
</body>
</html>"""
        return html

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters.

        Args:
            text: The text to escape.

        Returns:
            Escaped text.
        """
        # Don't escape too much - Mermaid needs certain characters
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
