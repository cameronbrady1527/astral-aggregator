# Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. PORT Environment Variable Issue

**Error:** `Error: Invalid value for '--port': '$PORT' is not a valid integer.`

**Cause:** The `$PORT` environment variable is not being properly expanded or is not set.

**Solutions:**

#### Option A: Use the Enhanced Shell Script (Recommended)
The `start.sh` script has been enhanced with better error handling and debugging:

```bash
# The script now includes:
# - Better environment variable validation
# - Fallback to port 8000 if PORT is not set
# - Detailed logging for debugging
```

#### Option B: Use Python Startup Script
If the shell script continues to fail, use the Python-based startup script:

```bash
# In Railway, you can override the startup command:
python start.py
```

#### Option C: Direct Uvicorn Command
As a last resort, you can use a direct uvicorn command in Railway:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
```

### 2. Debugging Deployment Issues

Run the debug script to get detailed information about your deployment environment:

```bash
python scripts/deploy_debug.py
```

This will show:
- Environment variables
- File system status
- Python path configuration
- App import status
- Uvicorn availability
- Port configuration

### 3. Railway-Specific Configuration

#### Environment Variables
Make sure these environment variables are set in Railway:
- `PORT` (automatically set by Railway)
- `PYTHONPATH=/app`
- `PYTHONUNBUFFERED=1`

#### Health Check Configuration
The health check is configured to use the root path (`/`). Make sure your FastAPI app has a root endpoint.

### 4. Alternative Deployment Commands

If the default startup script fails, try these alternatives in Railway:

#### Option 1: Python Startup Script
```bash
python start.py
```

#### Option 2: Direct Uvicorn with Fallback
```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level info
```

#### Option 3: Debug Mode
```bash
python scripts/deploy_debug.py && python start.py
```

### 5. Common Debugging Steps

1. **Check Environment Variables:**
   ```bash
   env | grep PORT
   ```

2. **Test App Import:**
   ```bash
   python -c "import app.main; print('App imported successfully')"
   ```

3. **Test Uvicorn:**
   ```bash
   python -m uvicorn app.main:app --help
   ```

4. **Check File Permissions:**
   ```bash
   ls -la start.sh start.py
   ```

### 6. Railway Configuration

The `railway.toml` file includes:
- Dockerfile-based build
- Health check configuration
- Environment-specific variables

If you need to override the startup command, uncomment the `startCommand` line in `railway.toml`:

```toml
startCommand = "python start.py"
```

### 7. Monitoring and Logs

- Check Railway logs for detailed error messages
- Use the debug script to gather environment information
- Monitor the health check endpoint at `/`

### 8. Fallback Strategies

If all else fails:

1. **Use a different port:** Hardcode port 8000 temporarily
2. **Simplify startup:** Use direct uvicorn command
3. **Check dependencies:** Ensure all requirements are installed
4. **Verify app structure:** Make sure `app/main.py` exists and is importable

## Quick Fix Commands

### For PORT Issues:
```bash
# Test current environment
python scripts/deploy_debug.py

# Use Python startup script
python start.py

# Direct uvicorn with fallback
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### For Import Issues:
```bash
# Test app import
python -c "import app.main"

# Check Python path
python -c "import sys; print(sys.path)"
```

### For Permission Issues:
```bash
# Make scripts executable
chmod +x start.sh start.py scripts/*.py
``` 