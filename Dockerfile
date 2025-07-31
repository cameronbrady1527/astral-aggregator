# Use Python 3.12 slim image optimized for Railway
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables for Railway
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x start.sh start.py scripts/railway_start.py scripts/healthcheck.py scripts/healthcheck.sh scripts/simple_healthcheck.py scripts/diagnose.py scripts/deploy_debug.py

# Create output directory with proper permissions
RUN mkdir -p output && chmod 755 output

# Expose port (Railway will override this)
EXPOSE 8000

# Use shell script for Railway deployment
CMD ["./start.sh"] 