# Scripts Directory

This directory contains deployment and utility scripts for the Astral Aggregator.

## Files

### `healthcheck.py`
Python-based health check script used by Docker containers to verify the application is running correctly.

**Features:**
- Tests `/ping` endpoint first (simpler)
- Falls back to `/` endpoint if ping fails
- Includes detailed error logging
- Retries with exponential backoff
- 10-second timeout per request

**Usage:**
```bash
python scripts/healthcheck.py
```

### `healthcheck.sh`
Bash-based health check script as a fallback for the Python script.

**Features:**
- Uses curl for HTTP requests
- Tests both `/ping` and `/` endpoints
- 10-second timeout per request
- 5 retry attempts with 15-second intervals

**Usage:**
```bash
./scripts/healthcheck.sh
```

## Docker Integration

These scripts are automatically used by the Dockerfile:

```dockerfile
# Health check with more lenient settings using Python script
HEALTHCHECK --interval=90s --timeout=30s --start-period=300s --retries=3 \
    CMD python scripts/healthcheck.py
```

## Railway Integration

Railway uses its own built-in health check against the `/ping` endpoint, but these scripts provide additional monitoring for Docker deployments.

## Troubleshooting

If health checks are failing:

1. **Check the logs** for detailed error messages
2. **Verify the app is running** on the correct port
3. **Test endpoints manually** using curl or a web browser
4. **Check environment variables** especially `PORT`

## Local Testing

For local testing of health endpoints, use the test script in the `tests/` directory:

```bash
python tests/test_healthcheck.py
``` 