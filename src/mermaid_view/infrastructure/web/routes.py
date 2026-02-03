"""FastAPI routes for MermaidView API."""

import base64
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

from mermaid_view import __version__
from mermaid_view.application.dtos.diagram_dto import (
    DiagramDTO,
    HealthDTO,
    RenderRequestDTO,
    RenderResponseDTO,
)
from mermaid_view.application.handlers.diagram_handler import DiagramHandler
from mermaid_view.domain.exceptions import DiagramNotFoundError, RenderError
from mermaid_view.domain.value_objects.render_config import OutputFormat, RenderConfig, Theme


def get_handler(request: Request) -> DiagramHandler:
    """Dependency to get the diagram handler."""
    return request.app.state.handler


def create_router() -> APIRouter:
    """Create the API router with all routes.

    Returns:
        Configured APIRouter.
    """
    router = APIRouter()

    # Health check
    @router.get("/health", response_model=HealthDTO, tags=["System"])
    async def health_check(request: Request) -> HealthDTO:
        """Check the health status of the service."""
        service = request.app.state.service
        renderer_available = await service._renderer.is_available()

        return HealthDTO(
            status="healthy",
            version=__version__,
            renderer_available=renderer_available,
        )

    # Root - Web interface
    @router.get("/", response_class=HTMLResponse, tags=["Web"])
    async def web_interface(request: Request) -> HTMLResponse:
        """Serve the web interface."""
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "version": __version__},
        )

    # API v1 routes
    api_router = APIRouter(prefix="/api/v1", tags=["API"])

    @api_router.post("/render", response_model=RenderResponseDTO)
    async def render_diagram(
        request_dto: RenderRequestDTO,
        handler: Annotated[DiagramHandler, Depends(get_handler)],
    ) -> RenderResponseDTO:
        """Render a Mermaid diagram.

        Args:
            request_dto: The render request with Mermaid code and options.
            handler: The diagram handler (injected).

        Returns:
            RenderResponseDTO with result.
        """
        return await handler.handle_render_request(request_dto)

    @api_router.post("/render/image", tags=["API"])
    async def render_diagram_image(
        request_dto: RenderRequestDTO,
        handler: Annotated[DiagramHandler, Depends(get_handler)],
    ) -> Response:
        """Render a Mermaid diagram and return the image directly.

        Args:
            request_dto: The render request with Mermaid code and options.
            handler: The diagram handler (injected).

        Returns:
            The rendered image.
        """
        try:
            config = RenderConfig(
                width=request_dto.width,
                height=request_dto.height,
                theme=request_dto.theme,
                output_format=request_dto.output_format,
                scale=request_dto.scale,
                transparent=request_dto.transparent,
                background_color=request_dto.background_color,
            )

            data = await handler.render_code_to_bytes(request_dto.code, config)

            media_type = (
                "image/png"
                if request_dto.output_format == OutputFormat.PNG
                else "image/svg+xml"
            )

            return Response(
                content=data,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"inline; filename=diagram.{request_dto.output_format.value}"
                },
            )

        except RenderError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Rendering failed: {e}")

    @api_router.get("/diagrams", response_model=list[DiagramDTO])
    async def list_diagrams(
        handler: Annotated[DiagramHandler, Depends(get_handler)],
    ) -> list[DiagramDTO]:
        """List all diagrams in memory.

        Args:
            handler: The diagram handler (injected).

        Returns:
            List of DiagramDTOs.
        """
        return handler.list_diagrams()

    @api_router.get("/diagrams/{diagram_id}", response_model=DiagramDTO)
    async def get_diagram(
        diagram_id: UUID,
        handler: Annotated[DiagramHandler, Depends(get_handler)],
    ) -> DiagramDTO:
        """Get a diagram by ID.

        Args:
            diagram_id: The diagram ID.
            handler: The diagram handler (injected).

        Returns:
            DiagramDTO with diagram data.
        """
        try:
            from mermaid_view.application.queries.get_diagram import GetDiagramQuery

            query = GetDiagramQuery(diagram_id=diagram_id)
            return await handler.handle_get_diagram_query(query)
        except DiagramNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @api_router.get("/diagrams/{diagram_id}/image")
    async def get_diagram_image(
        diagram_id: UUID,
        handler: Annotated[DiagramHandler, Depends(get_handler)],
    ) -> Response:
        """Get the rendered image for a diagram.

        Args:
            diagram_id: The diagram ID.
            handler: The diagram handler (injected).

        Returns:
            The rendered image.
        """
        diagram = handler.get_diagram(diagram_id)
        if not diagram:
            raise HTTPException(status_code=404, detail="Diagram not found")

        if not diagram.rendered_data:
            raise HTTPException(status_code=404, detail="Diagram not rendered")

        media_type = (
            "image/png"
            if diagram.config.output_format == OutputFormat.PNG
            else "image/svg+xml"
        )

        return Response(
            content=diagram.rendered_data,
            media_type=media_type,
        )

    # Quick render endpoint for simple GET requests
    class QuickRenderParams(BaseModel):
        """Query parameters for quick render."""

        code: str = Field(..., description="URL-encoded Mermaid code")
        theme: Theme = Field(default=Theme.DEFAULT)
        format: OutputFormat = Field(default=OutputFormat.PNG)
        width: int = Field(default=800, ge=100, le=4000)
        height: int = Field(default=600, ge=100, le=4000)

    @api_router.get("/quick-render")
    async def quick_render(
        code: Annotated[str, Query(description="URL-encoded Mermaid code")],
        handler: Annotated[DiagramHandler, Depends(get_handler)],
        theme: Theme = Theme.DEFAULT,
        format: OutputFormat = OutputFormat.PNG,
        width: int = 800,
        height: int = 600,
    ) -> Response:
        """Quick render endpoint for simple GET requests.

        Args:
            code: URL-encoded Mermaid code.
            handler: The diagram handler (injected).
            theme: Mermaid theme.
            format: Output format.
            width: Image width.
            height: Image height.

        Returns:
            The rendered image.
        """
        try:
            import urllib.parse

            decoded_code = urllib.parse.unquote(code)

            config = RenderConfig(
                width=width,
                height=height,
                theme=theme,
                output_format=format,
                scale=2.0,
            )

            data = await handler.render_code_to_bytes(decoded_code, config)

            media_type = "image/png" if format == OutputFormat.PNG else "image/svg+xml"

            return Response(
                content=data,
                media_type=media_type,
            )

        except RenderError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Rendering failed: {e}")

    router.include_router(api_router)

    return router
