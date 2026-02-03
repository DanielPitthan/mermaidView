# API Documentation

MermaidView provides a RESTful API for rendering Mermaid diagrams programmatically.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. For production deployments, consider adding authentication middleware.

## Endpoints

### Health Check

Check if the service is running and healthy.

```
GET /health
```

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "renderer_available": true
}
```

### Render Diagram (JSON Response)

Render a Mermaid diagram and get the result as JSON with base64-encoded image data.

```
POST /api/v1/render
```

**Request Body**
```json
{
  "code": "graph TD; A-->B",
  "width": 800,
  "height": 600,
  "theme": "default",
  "output_format": "png",
  "scale": 2.0,
  "transparent": false,
  "background_color": "white"
}
```

**Parameters**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `code` | string | Yes | - | Mermaid diagram code |
| `width` | integer | No | 800 | Output width (100-4000) |
| `height` | integer | No | 600 | Output height (100-4000) |
| `theme` | string | No | "default" | Theme: default, forest, dark, neutral |
| `output_format` | string | No | "png" | Format: png, svg |
| `scale` | float | No | 2.0 | Scale factor (0.5-4.0) |
| `transparent` | boolean | No | false | Transparent background |
| `background_color` | string | No | "white" | Background color |

**Response**
```json
{
  "success": true,
  "diagram_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Diagram rendered successfully",
  "data_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "content_type": "image/png"
}
```

**Error Response**
```json
{
  "success": false,
  "message": "Rendering failed",
  "error": "Invalid Mermaid syntax"
}
```

### Render Diagram (Image Response)

Render a Mermaid diagram and get the image directly.

```
POST /api/v1/render/image
```

**Request Body**
Same as `/api/v1/render`

**Response**
Binary image data with appropriate Content-Type header.

**Example with cURL**
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

### Quick Render

Render a diagram using GET request with query parameters.

```
GET /api/v1/quick-render
```

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `code` | string | Yes | - | URL-encoded Mermaid code |
| `theme` | string | No | "default" | Mermaid theme |
| `format` | string | No | "png" | Output format |
| `width` | integer | No | 800 | Width in pixels |
| `height` | integer | No | 600 | Height in pixels |

**Example**
```
GET /api/v1/quick-render?code=graph%20TD%3B%20A-%3EB&theme=dark&format=png
```

### List Diagrams

Get all rendered diagrams in memory.

```
GET /api/v1/diagrams
```

**Response**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "code": "graph TD; A-->B",
    "diagram_type": "flowchart",
    "name": null,
    "description": null,
    "width": 800,
    "height": 600,
    "theme": "default",
    "output_format": "png",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "is_rendered": true
  }
]
```

### Get Diagram by ID

Retrieve a specific diagram by its ID.

```
GET /api/v1/diagrams/{diagram_id}
```

**Response**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "code": "graph TD; A-->B",
  "diagram_type": "flowchart",
  "name": null,
  "description": null,
  "width": 800,
  "height": 600,
  "theme": "default",
  "output_format": "png",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "is_rendered": true
}
```

### Get Diagram Image

Get the rendered image for a specific diagram.

```
GET /api/v1/diagrams/{diagram_id}/image
```

**Response**
Binary image data.

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Diagram not found |
| 422 | Validation Error - Invalid parameters |
| 500 | Server Error - Rendering failed |

## Rate Limiting

No rate limiting is implemented by default. For production use, consider adding rate limiting middleware.

## Examples

### Python

```python
import httpx

async def render_diagram():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/render/image",
            json={
                "code": "graph TD; A-->B; B-->C",
                "theme": "dark",
                "output_format": "png"
            }
        )
        
        with open("diagram.png", "wb") as f:
            f.write(response.content)
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8000/api/v1/render/image', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    code: 'graph TD; A-->B; B-->C',
    theme: 'default',
    output_format: 'png'
  })
});

const blob = await response.blob();
// Save or display the image
```

### cURL

```bash
# Render to PNG file
curl -X POST http://localhost:8000/api/v1/render/image \
  -H "Content-Type: application/json" \
  -d '{"code": "sequenceDiagram\nAlice->>Bob: Hello"}' \
  -o sequence.png

# Get JSON response with base64
curl -X POST http://localhost:8000/api/v1/render \
  -H "Content-Type: application/json" \
  -d '{"code": "graph TD; A-->B"}'
```

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
