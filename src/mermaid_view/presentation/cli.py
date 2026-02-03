"""Command Line Interface for MermaidView."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from mermaid_view import __version__
from mermaid_view.application.commands.render_diagram import RenderDiagramCommand
from mermaid_view.application.handlers.diagram_handler import DiagramHandler
from mermaid_view.domain.services.diagram_service import DiagramService
from mermaid_view.domain.value_objects.render_config import OutputFormat, RenderConfig, Theme
from mermaid_view.infrastructure.adapters.file_storage import FileStorage
from mermaid_view.infrastructure.adapters.mermaid_ink_renderer import MermaidInkRenderer
from mermaid_view.infrastructure.adapters.playwright_renderer import PlaywrightRenderer
from mermaid_view.infrastructure.config import AppConfig, get_config

# Create Typer app
app = typer.Typer(
    name="mermaid-view",
    help="MermaidView - Visualize and export Mermaid diagrams to PNG",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"MermaidView version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """MermaidView - A tool for visualizing Mermaid diagrams."""
    pass


@app.command()
def render(
    input_file: Optional[Path] = typer.Argument(
        None,
        help="Input .mmd file containing Mermaid code",
        exists=True,
        readable=True,
    ),
    code: Optional[str] = typer.Option(
        None,
        "--code",
        "-c",
        help="Mermaid code to render (alternative to input file)",
    ),
    output: Path = typer.Option(
        Path("output.png"),
        "--output",
        "-o",
        help="Output file path",
    ),
    width: int = typer.Option(
        800,
        "--width",
        "-w",
        help="Output width in pixels",
        min=100,
        max=4000,
    ),
    height: int = typer.Option(
        600,
        "--height",
        "-h",
        help="Output height in pixels",
        min=100,
        max=4000,
    ),
    theme: Theme = typer.Option(
        Theme.DEFAULT,
        "--theme",
        "-t",
        help="Mermaid theme",
        case_sensitive=False,
    ),
    scale: float = typer.Option(
        2.0,
        "--scale",
        "-s",
        help="Scale factor for higher resolution",
        min=0.5,
        max=4.0,
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.PNG,
        "--format",
        "-f",
        help="Output format",
        case_sensitive=False,
    ),
    transparent: bool = typer.Option(
        False,
        "--transparent",
        help="Use transparent background",
    ),
    use_fallback: bool = typer.Option(
        True,
        "--use-fallback/--no-fallback",
        help="Use mermaid.ink as fallback if Playwright fails",
    ),
) -> None:
    """Render a Mermaid diagram to an image file.

    Examples:
        mermaid-view render diagram.mmd -o output.png
        mermaid-view render --code "graph TD; A-->B" -o output.png
        mermaid-view render diagram.mmd -t dark -w 1200 -h 800
    """
    # Get mermaid code
    if input_file:
        try:
            mermaid_code = input_file.read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            raise typer.Exit(1)
    elif code:
        mermaid_code = code
    else:
        console.print("[red]Error: Either input file or --code must be provided[/red]")
        raise typer.Exit(1)

    # Show preview
    console.print(Panel(
        Syntax(mermaid_code, "text", theme="monokai", line_numbers=True),
        title="Mermaid Code",
        border_style="blue",
    ))

    # Run async render
    asyncio.run(_render_diagram(
        code=mermaid_code,
        output_path=output,
        width=width,
        height=height,
        theme=theme,
        scale=scale,
        output_format=format,
        transparent=transparent,
        use_fallback=use_fallback,
    ))


async def _render_diagram(
    code: str,
    output_path: Path,
    width: int,
    height: int,
    theme: Theme,
    scale: float,
    output_format: OutputFormat,
    transparent: bool,
    use_fallback: bool,
) -> None:
    """Async function to render diagram."""
    config = get_config()

    # Create adapters
    playwright_renderer = PlaywrightRenderer(
        timeout=config.renderer_timeout,
        headless=config.headless,
    )

    fallback_renderer = MermaidInkRenderer() if use_fallback else None
    storage = FileStorage(output_dir=config.output_dir)

    # Create service
    service = DiagramService(
        renderer=playwright_renderer,
        storage=storage,
        fallback_renderer=fallback_renderer,
    )

    # Create render config
    render_config = RenderConfig(
        width=width,
        height=height,
        theme=theme,
        output_format=output_format,
        scale=scale,
        transparent=transparent,
        background_color="transparent" if transparent else "white",
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Rendering diagram...", total=None)

        try:
            async with service:
                result_path = await service.render_code_and_save(
                    code=code,
                    output_path=output_path,
                    config=render_config,
                )

            progress.update(task, description="[green]Done!")
            console.print(f"\n[green]Success![/green] Diagram saved to: [bold]{result_path}[/bold]")

        except Exception as e:
            progress.update(task, description="[red]Failed!")
            console.print(f"\n[red]Error:[/red] {e}")
            raise typer.Exit(1)


@app.command()
def serve(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        help="Host to bind to",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to listen on",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto-reload for development",
    ),
) -> None:
    """Start the web server.

    Examples:
        mermaid-view serve
        mermaid-view serve --port 3000
        mermaid-view serve --reload
    """
    import uvicorn

    from mermaid_view.infrastructure.web.app import create_app

    console.print(Panel(
        f"Starting MermaidView server at [bold]http://{host}:{port}[/bold]",
        title="MermaidView Server",
        border_style="green",
    ))

    uvicorn.run(
        "mermaid_view.infrastructure.web.app:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


@app.command()
def info() -> None:
    """Show information about MermaidView."""
    table = Table(title="MermaidView Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Version", __version__)
    table.add_row("Python", sys.version.split()[0])

    # Check Playwright availability
    try:
        import playwright
        playwright_version = getattr(playwright, "__version__", "installed")
        table.add_row("Playwright", playwright_version)
    except ImportError:
        table.add_row("Playwright", "[red]not installed[/red]")

    # Configuration
    config = get_config()
    table.add_row("Output Directory", str(config.output_dir))
    table.add_row("Default Theme", config.default_theme)
    table.add_row("Default Size", f"{config.default_width}x{config.default_height}")

    console.print(table)


@app.command()
def example() -> None:
    """Show example Mermaid diagrams."""
    examples = [
        ("Flowchart", """graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B"""),
        ("Sequence Diagram", """sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob!
    Bob-->>Alice: Hi Alice!"""),
        ("Class Diagram", """classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()"""),
        ("State Diagram", """stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]"""),
    ]

    for name, code in examples:
        console.print(Panel(
            Syntax(code, "text", theme="monokai"),
            title=name,
            border_style="blue",
        ))
        console.print()


if __name__ == "__main__":
    app()
