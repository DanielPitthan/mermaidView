# MermaidView Dockerfile
# Multi-stage build for optimized image size

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-slim as runtime

# Labels
LABEL maintainer="MermaidView Team"
LABEL description="MermaidView - Mermaid Diagram Visualizer"
LABEL version="1.0.0"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    MERMAID_VIEW_HOST=0.0.0.0 \
    MERMAID_VIEW_PORT=8000 \
    MERMAID_VIEW_HEADLESS=true \
    MERMAID_VIEW_OUTPUT_DIR=/app/output \
    MERMAID_VIEW_DIAGRAMS_DIR=/app/diagrams

WORKDIR /app

# Install runtime dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    # Fonts
    fonts-liberation \
    fonts-noto-color-emoji \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY src/ /app/src/
COPY pyproject.toml /app/
COPY README.md /app/

# Install the package in editable mode
RUN pip install -e .

# Create directories for output and diagrams
RUN mkdir -p /app/output /app/diagrams && \
    chmod 777 /app/output /app/diagrams

# Create non-root user for security
RUN useradd -m -u 1000 mermaid && \
    chown -R mermaid:mermaid /app
USER mermaid

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Default command - start web server
CMD ["mermaid-view", "serve", "--host", "0.0.0.0", "--port", "8000"]
