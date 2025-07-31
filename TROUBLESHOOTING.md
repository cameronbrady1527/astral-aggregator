# Deployment Troubleshooting Guide

This guide helps resolve common deployment issues with the Astral Aggregator on Railway.

## Health Check Issues

### Problem: "Attempt #1 failed with service unavailable"

**Symptoms:**
- Health checks fail during deployment
- App shows as "unhealthy" in Railway dashboard
- Deployment times out

**Solutions:**

1. **Check Railway Logs**
   ```bash
   # View deployment logs
   railway logs
   ```

2. **Verify Environment Variables**
   - Ensure `FIRECRAWL_API_KEY` is set
   - Check that `PORT` is available (Railway provides this)
   - Verify `PYTHONPATH=/app` is set

3. **Test Health Endpoints Manually**
   ```bash
   # Test ping endpoint
   curl https://your-app.railway.app/ping
   
   # Test health endpoint
   curl https://your-app.railway.app/health
   
   # Test root endpoint
   curl https://your-app.railway.app/
   ```

4. **Check Startup Process**
   - The startup script (`start.sh`) provides detailed debugging
   - Look for import errors or missing dependencies
   - Check if the app starts successfully

### Health Check Configuration

The app has multiple health check mechanisms:

1. **Railway Health Check**: Uses `/ping` endpoint
2. **Docker Health Check**: Uses `healthcheck.sh` script
3. **Fallback Health Check**: Uses `healthcheck.py` script

**Health Check Settings:**
- **Start Period**: 180 seconds (3 minutes)
- **Interval**: 60 seconds
- **Timeout**: 30 seconds
- **Retries**: 5 attempts

## Common Issues

### 1. Import Errors

**Problem**: App fails to import modules
**Solution**: Check that all dependencies are in `requirements.txt`

### 2. Port Binding Issues

**Problem**: App can't bind to port
**Solution**: Ensure app listens on `0.0.0.0:$PORT`

### 3. Environment Variable Issues

**Problem**: App can't find required variables
**Solution**: Set variables in Railway dashboard

### 4. Database Connection Issues

**Problem**: Can't connect to PostgreSQL
**Solution**: Add PostgreSQL service in Railway

## Debugging Steps

### 1. Check Build Logs
```bash
railway logs --build
```

### 2. Check Runtime Logs
```bash
railway logs
```

### 3. Test Locally
```bash
# Test app import
python -c "import app.main; print('OK')"

# Test health endpoints
python -c "
from app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
print('Ping:', client.get('/ping').status_code)
print('Health:', client.get('/health').status_code)
"
```

### 4. Check Health Check Script
```bash
# Test health check script
python healthcheck.py
```

## Railway-Specific Issues

### 1. Build Failures
- Check Dockerfile syntax
- Verify all files are present
- Check requirements.txt

### 2. Service Unavailable
- Check if app is starting correctly
- Verify health check endpoints
- Check environment variables

### 3. Timeout Issues
- Increase health check timeouts
- Check app startup time
- Verify dependencies

## Quick Fixes

### Reset Deployment
```bash
railway service restart
```

### Redeploy
```bash
railway up
```

### Check Status
```bash
railway status
```

## Support

If issues persist:

1. **Check Railway Status**: [status.railway.app](https://status.railway.app)
2. **Railway Docs**: [docs.railway.app](https://docs.railway.app)
3. **Community**: [discord.gg/railway](https://discord.gg/railway)

## Health Check Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/ping` | Simple health check | `{"pong": "ok"}` |
| `/health` | Detailed health check | `{"status": "healthy", "service": "astral-api", "version": "0.0.1"}` |
| `/` | Root endpoint | Full app info |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FIRECRAWL_API_KEY` | Yes | Your Firecrawl API key |
| `PORT` | No | Port (Railway provides) |
| `PYTHONPATH` | No | Python path (set to `/app`) |
| `LOG_LEVEL` | No | Logging level (default: INFO) | 