# Base Python 3.11 slim image for minimal footprint and reproducible benchmarking
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Install curl for healthcheck probe and GMT console flow commands
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Expose standard application port
EXPOSE 5000

# Docker healthcheck endpoint used by GMT ScenarioRunner
HEALTHCHECK --interval=2s --timeout=3s --retries=10 --start-period=2s \
    CMD curl -f http://localhost:5000/health || exit 1

# Start production-ready WSGI server (Gunicorn) listening on all interfaces
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--access-logfile", "-", "app:app"]
