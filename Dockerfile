# =============================================================================
# SpokeStack Agent Service - Multi-Stage Docker Build
# =============================================================================
# This Dockerfile creates a production-ready container for the SpokeStack
# multi-tenant AI agent platform.
#
# Build:   docker build -t spokestack-agents .
# Run:     docker run -p 8000:8000 --env-file .env spokestack-agents
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Production
# -----------------------------------------------------------------------------
FROM python:3.11-slim as production

# Labels
LABEL maintainer="SpokeStack Team"
LABEL description="Multi-tenant AI agent platform"
LABEL version="1.0.0"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash spokestack

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/spokestack/.local

# Copy application code
COPY --chown=spokestack:spokestack . .

# Set environment
ENV PATH=/home/spokestack/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER spokestack

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
