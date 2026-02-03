# Usage Guide

This guide covers all the ways to use MermaidView for rendering Mermaid diagrams.

## Table of Contents

1. [Installation](#installation)
2. [CLI Usage](#cli-usage)
3. [Web Interface](#web-interface)
4. [API Usage](#api-usage)
5. [Docker Usage](#docker-usage)
6. [Configuration](#configuration)
7. [Mermaid Diagram Examples](#mermaid-diagram-examples)

## Installation

### From Source

```bash
# Clone repository
git clone https://github.com/yourusername/mermaidview.git
cd mermaidview

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install package
pip install -e .

# Install Playwright browser
playwright install chromium
```

### Using Docker

```bash
docker-compose up --build
```

## CLI Usage

### Render from file

Create a file `diagram.mmd`:
```
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[OK]
    B -->|No| D[Cancel]
```

Render it:
```bash
mermaid-view render diagram.mmd -o output.png
```

### Render from inline code

```bash
mermaid-view render --code "graph TD; A-->B" -o output.png
```

### Render with options

```bash
# Dark theme, high resolution
mermaid-view render diagram.mmd \
  --theme dark \
  --width 1200 \
  --height 800 \
  --scale 2.0 \
  -o output.png

# SVG output
mermaid-view render diagram.mmd \
  --format svg \
  -o output.svg

# Transparent background
mermaid-view render diagram.mmd \
  --transparent \
  -o output.png
```

### Available themes

- `default` - Light theme (default)
- `forest` - Green tones
- `dark` - Dark theme
- `neutral` - Gray tones

### Show examples

```bash
mermaid-view example
```

### Show version and info

```bash
mermaid-view --version
mermaid-view info
```

## Web Interface

### Start the server

```bash
mermaid-view serve --port 8000
```

### Access the interface

Open http://localhost:8000 in your browser.

### Features

1. **Code Editor**: Write or paste Mermaid code
2. **Live Preview**: See the rendered diagram in real-time
3. **Theme Selection**: Switch between themes
4. **Download**: Export as PNG or SVG
5. **Examples**: Quick-load example diagrams

### Keyboard shortcuts

- `Ctrl+Enter`: Render diagram

## API Usage

### Start the API server

```bash
mermaid-view serve --port 8000
```

### Render and download image

```bash
curl -X POST http://localhost:8000/api/v1/render/image \
  -H "Content-Type: application/json" \
  -d '{
    "code": "graph TD\n    A[Start] --> B[End]",
    "theme": "default",
    "output_format": "png",
    "width": 800,
    "height": 600
  }' \
  --output diagram.png
```

### Render and get JSON response

```bash
curl -X POST http://localhost:8000/api/v1/render \
  -H "Content-Type: application/json" \
  -d '{"code": "graph TD; A-->B"}'
```

### Python example

```python
import httpx
import base64

async def render_and_save():
    async with httpx.AsyncClient() as client:
        # Option 1: Get image directly
        response = await client.post(
            "http://localhost:8000/api/v1/render/image",
            json={
                "code": """
                    sequenceDiagram
                        Alice->>Bob: Hello!
                        Bob-->>Alice: Hi!
                """,
                "theme": "dark"
            }
        )
        with open("sequence.png", "wb") as f:
            f.write(response.content)
        
        # Option 2: Get JSON with base64
        response = await client.post(
            "http://localhost:8000/api/v1/render",
            json={"code": "pie title Pets\n\"Dogs\" : 386\n\"Cats\" : 85"}
        )
        data = response.json()
        if data["success"]:
            image_bytes = base64.b64decode(data["data_base64"])
            with open("pie.png", "wb") as f:
                f.write(image_bytes)
```

### JavaScript/Fetch example

```javascript
async function renderDiagram(code, filename) {
    const response = await fetch('http://localhost:8000/api/v1/render/image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            code: code,
            theme: 'default',
            output_format: 'png'
        })
    });
    
    const blob = await response.blob();
    
    // Download in browser
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
}

renderDiagram('graph TD; A-->B', 'diagram.png');
```

## Docker Usage

### Using docker-compose

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### Using docker directly

```bash
# Build image
docker build -t mermaid-view -f docker/Dockerfile .

# Run container
docker run -d \
  --name mermaid-view \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  mermaid-view

# Stop container
docker stop mermaid-view
```

### Environment variables in Docker

```bash
docker run -d \
  -e MERMAID_VIEW_THEME=dark \
  -e MERMAID_VIEW_WIDTH=1200 \
  -e MERMAID_VIEW_SCALE=2.0 \
  -p 8000:8000 \
  mermaid-view
```

## Configuration

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MERMAID_VIEW_HOST` | `0.0.0.0` | Server bind host |
| `MERMAID_VIEW_PORT` | `8000` | Server port |
| `MERMAID_VIEW_DEBUG` | `false` | Debug mode |
| `MERMAID_VIEW_HEADLESS` | `true` | Run browser headless |
| `MERMAID_VIEW_TIMEOUT` | `30000` | Render timeout (ms) |
| `MERMAID_VIEW_USE_FALLBACK` | `true` | Use mermaid.ink fallback |
| `MERMAID_VIEW_OUTPUT_DIR` | `output` | Output directory |
| `MERMAID_VIEW_DIAGRAMS_DIR` | `diagrams` | Diagrams directory |
| `MERMAID_VIEW_THEME` | `default` | Default theme |
| `MERMAID_VIEW_WIDTH` | `800` | Default width |
| `MERMAID_VIEW_HEIGHT` | `600` | Default height |
| `MERMAID_VIEW_SCALE` | `2.0` | Default scale factor |

### Example: Set environment variables

```bash
# Linux/macOS
export MERMAID_VIEW_THEME=dark
export MERMAID_VIEW_SCALE=3.0
mermaid-view serve

# Windows PowerShell
$env:MERMAID_VIEW_THEME = "dark"
$env:MERMAID_VIEW_SCALE = "3.0"
mermaid-view serve
```

## Mermaid Diagram Examples

### Flowchart

```
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B
    C --> E[End]
```

### Sequence Diagram

```
sequenceDiagram
    participant Alice
    participant Bob
    participant Charlie
    
    Alice->>Bob: Hello Bob!
    Bob-->>Alice: Hi Alice!
    Alice->>Charlie: Hi Charlie!
    Charlie-->>Alice: Hey!
```

### Class Diagram

```
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
```

### State Diagram

```
stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```

### ER Diagram

```
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
```

### Gantt Chart

```
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Planning
    Research           :a1, 2024-01-01, 30d
    Design             :after a1, 20d
    section Development
    Implementation     :2024-02-20, 45d
    Testing            :15d
```

### Pie Chart

```
pie title Pets adopted
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```

### Git Graph

```
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
```

For more diagram types and syntax, visit the [Mermaid documentation](https://mermaid.js.org/).

## Troubleshooting

### Playwright not installed

```bash
playwright install chromium
```

### Permission denied on output directory

```bash
chmod 755 output/
```

### Docker: Browser crashes

Ensure the container has enough memory:
```bash
docker run -m 2g ...
```

### Timeout errors

Increase the timeout:
```bash
export MERMAID_VIEW_TIMEOUT=60000
```

Or use the mermaid.ink fallback:
```bash
export MERMAID_VIEW_USE_FALLBACK=true
```
