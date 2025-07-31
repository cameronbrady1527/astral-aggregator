# PORT Environment Variable Issue - Quick Fix Guide

## Current Issue
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

This error indicates that the `$PORT` environment variable is not being expanded properly.

## Immediate Solutions

### Solution 1: Use Python Startup Script (Recommended)
The `railway.toml` file has been updated to use `python start.py` as the startup command. This should resolve the issue.

### Solution 2: Use Simple Startup Script
If the main Python script fails, try the simplified version:

In `railway.toml`, change:
```toml
startCommand = "python start_simple.py"
```

### Solution 3: Direct Uvicorn Command
As a last resort, use the direct uvicorn command:

In `railway.toml`, change:
```toml
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"
```

## Railway Dashboard Configuration

If the `railway.toml` changes don't work, you can override the startup command directly in the Railway dashboard:

1. Go to your Railway project dashboard
2. Navigate to the service settings
3. Find the "Start Command" field
4. Enter one of these commands:

```bash
# Option 1: Python startup script
python start.py

# Option 2: Simple startup script
python start_simple.py

# Option 3: Direct uvicorn with fallback
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1

# Option 4: Hardcoded port (temporary fix)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## Debugging Steps

### 1. Check Environment Variables
Run this in Railway shell or add to startup script:
```bash
env | grep PORT
```

### 2. Test Port Expansion
```bash
echo "PORT: ${PORT:-8000}"
```

### 3. Verify Startup Script
```bash
python start.py
```

## Why This Happens

1. **Shell Script Execution**: Railway might not be executing shell scripts properly
2. **Environment Variable Expansion**: The `$PORT` variable isn't being expanded before being passed to uvicorn
3. **Startup Command Override**: Railway might be using a different startup command than specified in the Dockerfile

## Prevention

The updated configuration files now include:
- Multiple startup script options
- Better error handling
- Fallback port configuration
- Comprehensive debugging tools

## Quick Test Commands

Test these locally to ensure they work:

```bash
# Test Python startup script
python start.py

# Test simple startup script
python start_simple.py

# Test direct uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## Next Steps

1. Deploy with the updated `railway.toml` configuration
2. If it still fails, try the Railway dashboard override
3. Use the debug script to gather more information: `python scripts/deploy_debug.py`
4. Check Railway logs for detailed error messages

## Fallback Strategy

If all else fails:
1. Use hardcoded port 8000 temporarily
2. Contact Railway support with the debug information
3. Consider using a different deployment platform temporarily 