# Use Python 3.12 slim image optimized for Railway
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables for Railway
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

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
RUN chmod +x start.sh healthcheck.py healthcheck.sh

# Create output directory with proper permissions
RUN mkdir -p output && chmod 755 output

# Expose port (Railway will override this)
EXPOSE 8000

# Health check with more lenient settings using bash script
HEALTHCHECK --interval=60s --timeout=30s --start-period=180s --retries=5 \
    CMD ./healthcheck.sh

# Run the application with Railway-specific settings
CMD ["./start.sh"] 