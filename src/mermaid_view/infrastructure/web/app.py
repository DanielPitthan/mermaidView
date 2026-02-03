"""FastAPI application factory."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mermaid_view import __version__
from mermaid_view.application.handlers.diagram_handler import DiagramHandler
from mermaid_view.domain.services.diagram_service import DiagramService
from mermaid_view.infrastructure.adapters.file_storage import FileStorage
from mermaid_view.infrastructure.adapters.mermaid_ink_renderer import MermaidInkRenderer
from mermaid_view.infrastructure.adapters.playwright_renderer import PlaywrightRenderer
from mermaid_view.infrastructure.config import get_config
from mermaid_view.infrastructure.web.routes import create_router

# Get templates and static directories
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application.
    """
    config = get_config()

    # Create adapters
    playwright_renderer = PlaywrightRenderer(
        timeout=config.renderer_timeout,
        headless=config.headless,
    )
    fallback_renderer = MermaidInkRenderer() if config.use_fallback else None
    storage = FileStorage(
        output_dir=config.output_dir,
        diagrams_dir=config.diagrams_dir,
    )

    # Create service and handler
    service = DiagramService(
        renderer=playwright_renderer,
        storage=storage,
        fallback_renderer=fallback_renderer,
    )
    handler = DiagramHandler(service)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan handler."""
        # Startup
        await service.initialize()
        yield
        # Shutdown
        await service.cleanup()

    # Create FastAPI app
    app = FastAPI(
        title="MermaidView API",
        description="API for rendering Mermaid diagrams to PNG/SVG",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store dependencies in app state
    app.state.service = service
    app.state.handler = handler
    app.state.config = config
    app.state.templates = Jinja2Templates(directory=TEMPLATES_DIR)

    # Mount static files directory
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Create and include router
    router = create_router()
    app.include_router(router)

    return app
