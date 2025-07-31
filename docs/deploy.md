# Deployment Guide

## Railway Deployment

This guide covers deploying the Astral Aggregator to Railway.

### Quick Deploy

1. **Connect Repository**: Link your GitHub repository to Railway
2. **Configure Environment**: Set required environment variables
3. **Deploy**: Railway will automatically build and deploy using the Dockerfile

### Environment Variables

Required variables for Railway:

```bash
# API Keys (required for Firecrawl detection)
FIRECRAWL_API_KEY=your_api_key_here

# Optional: Logging
LOG_LEVEL=INFO
```

**Important**: The `FIRECRAWL_API_KEY` environment variable is required. If not set, the app will still start but Firecrawl detection will fail.

### Health Check Configuration

The app includes multiple health check mechanisms:

1. **Railway Health Check**: Uses `/ping` endpoint (configured in `railway.toml`)
2. **Docker Health Check**: Uses custom `scripts/healthcheck.py` script
3. **Manual Testing**: Use `tests/test_healthcheck.py` for local testing

**Health Check Endpoints:**
- `/ping` - Simple ping response (`{"pong": "ok"}`)
- `/health` - Detailed health status
- `/` - Root endpoint with API information

### File Structure

```
aggregator/
├── app/                    # Main application code
├── scripts/               # Deployment and utility scripts
│   ├── healthcheck.py     # Python health check script
│   └── healthcheck.sh     # Bash health check script
├── tests/                 # Test files
│   ├── test_healthcheck.py # Local health check testing
│   └── ...                # Other test files
├── Dockerfile             # Container configuration
├── railway.toml           # Railway deployment config
└── start.sh              # Application startup script
```

### Troubleshooting

#### 1. Health Check Failures
**Problem**: Health checks fail after deployment
**Symptoms**: 
- Railway shows "Health check failed"
- App appears to be running but health checks timeout

**Solution**: 
- ✅ **Fixed**: Added missing `requests` dependency to `requirements.txt`
- ✅ **Fixed**: Updated configuration to use environment variables properly
- ✅ **Fixed**: Improved healthcheck script with better error handling
- ✅ **Fixed**: Increased healthcheck timeouts and start periods
- ✅ **Fixed**: Added graceful error handling in health endpoints
- ✅ **Fixed**: Improved startup script with configuration validation

**Recent Health Check Improvements:**
- Added missing `requests>=2.31.0` dependency
- Updated config to use `${FIRECRAWL_API_KEY}` environment variable
- Increased Railway healthcheck timeout to 600 seconds
- Increased Docker healthcheck start period to 10 minutes
- Added port availability checking in healthcheck script
- Added 30-second startup delay in healthcheck script
- Improved error handling in all health endpoints
- Added configuration validation in startup script

#### 2. Build Failures
**Problem**: Docker build fails
**Solution**: 
- Check the build logs in Railway dashboard
- Ensure all dependencies are in `requirements.txt` (now includes `requests`)
- Verify the Dockerfile syntax
- The startup script provides detailed debugging information

#### 3. Environment Variables
**Problem**: App can't find required variables
**Solution**:
- Set `FIRECRAWL_API_KEY` in Railway dashboard
- The app will start even without the API key (Firecrawl detection will just fail)
- Check the startup logs for variable loading

#### 4. Port Issues
**Problem**: App not accessible
**Solution**:
- Railway automatically provides the `PORT` environment variable
- Ensure your app listens on `0.0.0.0:$PORT`
- Check the service logs for port binding errors
- The startup script handles port configuration automatically

#### 5. Database Connection
**Problem**: Can't connect to PostgreSQL
**Solution**:
- Verify `DATABASE_URL` is set correctly
- Check if the database service is running
- Ensure your app handles database connection gracefully
- The lazy initialization prevents startup failures

### Debugging Commands

```bash
# View logs
railway logs

# Check service status
railway status

# Restart service
railway service restart

# Open shell in container
railway shell
```

### Health Check Debugging

The app includes multiple health check mechanisms:

1. **Railway Health Check**: Uses `/ping` endpoint (simplest)
2. **Docker Health Check**: Uses custom `scripts/healthcheck.py` script
3. **Manual Testing**: You can test endpoints manually

If health checks are failing:

1. **Check Railway Logs**: Look for startup errors
2. **Test Endpoints Manually**: Visit `/ping` and `/health` in browser
3. **Check Environment Variables**: Ensure `FIRECRAWL_API_KEY` is set
4. **Review Startup Script**: The script provides detailed debugging output
5. **Use Local Test Script**: Run `python tests/test_healthcheck.py` after starting the app locally
6. **Run Deployment Test**: Use `python test_deployment.py` to verify all components

### Pre-Deployment Testing

Before deploying, you can run the deployment test script to verify everything works:

```bash
python test_deployment.py
```

This script tests:
- ✅ All required dependencies are available
- ✅ Configuration loading works correctly
- ✅ App can be imported without errors
- ✅ Health endpoints respond correctly
- ✅ Healthcheck script runs without crashing

## Cost Optimization

### Railway Pricing
- **Starter Plan**: $5/month (recommended for your use case)
- **Pro Plan**: $20/month (for higher traffic)
- **Enterprise**: Custom pricing

### Cost-Saving Tips
1. **Use Starter Plan**: Perfect for development and moderate usage
2. **Optimize Builds**: The provided Dockerfile is optimized for faster builds
3. **Monitor Usage**: Check Railway dashboard for resource usage
4. **Scale Down**: Reduce replicas during low-traffic periods

## Production Considerations

### Security
- All environment variables are encrypted
- Automatic SSL certificates
- Secure database connections
- No need to manage secrets manually

### Performance
- Global CDN included
- Automatic load balancing
- Built-in caching layers
- Optimized container images

### Backup & Recovery
- Automatic database backups (if using Railway PostgreSQL)
- Easy rollback to previous deployments
- Git-based version control 