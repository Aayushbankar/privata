# MOSDAC AI Help Bot - Flask Frontend Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r mosdac && useradd -r -g mosdac mosdac

# Create application directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/static /app/templates && \
    chown -R mosdac:mosdac /app

# Copy application code
COPY --chown=mosdac:mosdac . .

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for Redis to be ready\n\
echo "Waiting for Redis..."\n\
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do\n\
  sleep 1\n\
done\n\
echo "Redis is ready!"\n\
\n\
# Initialize application\n\
echo "Initializing application..."\n\
python -c "from app import create_app; app = create_app(); print(\"App initialized successfully\")"\n\
\n\
# Start application\n\
echo "Starting MOSDAC Flask Frontend..."\n\
exec gunicorn --bind 0.0.0.0:5000 \\\n\
    --workers ${WORKERS:-4} \\\n\
    --worker-class gevent \\\n\
    --worker-connections ${WORKER_CONNECTIONS:-1000} \\\n\
    --timeout ${TIMEOUT:-30} \\\n\
    --keepalive ${KEEPALIVE:-5} \\\n\
    --max-requests ${MAX_REQUESTS:-1000} \\\n\
    --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} \\\n\
    --preload \\\n\
    --access-logfile - \\\n\
    --error-logfile - \\\n\
    --log-level ${LOG_LEVEL:-info} \\\n\
    "app:create_app()"\n' > /app/start.sh && \
    chmod +x /app/start.sh

# Install netcat for health checks
RUN apt-get update && apt-get install -y netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER mosdac

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["/app/start.sh"]

# Labels for metadata
LABEL maintainer="MOSDAC AI Help Bot Team" \
      version="2.0.0" \
      description="Flask Frontend for MOSDAC AI Help Bot" \
      org.opencontainers.image.title="MOSDAC Flask Frontend" \
      org.opencontainers.image.description="Enhanced Flask frontend with comprehensive middleware" \
      org.opencontainers.image.version="2.0.0" \
      org.opencontainers.image.vendor="ISRO MOSDAC" \
      org.opencontainers.image.source="https://github.com/mosdac/ai-help-bot"
