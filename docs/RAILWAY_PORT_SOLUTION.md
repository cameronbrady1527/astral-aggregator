# Railway PORT Environment Variable Solution

## Problem Analysis

The deployment is failing with:
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

This indicates that Railway is passing the literal string `$PORT` instead of expanding the environment variable.

## Root Cause

Based on Railway documentation and common deployment patterns, the issue is likely one of these:

1. **Railway Environment Variable Expansion**: Railway's environment variable expansion mechanism is not working properly
2. **Startup Method Conflict**: There's a conflict between different startup methods
3. **Shell vs Python Environment**: The environment variable expansion differs between shell and Python contexts

## Railway Best Practices

### 1. Use Simple Startup Commands
Railway works best with simple, direct startup commands. Complex scripts can cause environment variable expansion issues.

### 2. Let Railway Handle PORT Automatically
Railway automatically provides the `PORT` environment variable. The application should use it directly without complex fallback logic.

### 3. Avoid Custom startCommand When Possible
Railway's default behavior (using Dockerfile CMD) is often more reliable than custom startCommand.

## Solutions Implemented

### Solution 1: Railway Python Script (`scripts/railway_start.py`)
```python
#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("Starting Astral Aggregator...")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/app'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Get PORT with fallback
    port = os.environ.get('PORT', '8000')
    print(f"Using port: {port}")
    
    # Start uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', port,
        '--workers', '1'
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
```

### Solution 2: Shell Script (`start.sh`)
```bash
#!/bin/bash
set -e

echo "🚀 Starting Astral Aggregator..."

# Set environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Create output directory
mkdir -p output

# Get PORT with explicit expansion and validation
PORT_NUM="${PORT:-8000}"

# Validate PORT is a number
if [[ ! "$PORT_NUM" =~ ^[0-9]+$ ]]; then
    echo "❌ PORT '$PORT_NUM' is not a valid number, using 8000"
    PORT_NUM=8000
fi

echo "🎯 Final port configuration: $PORT_NUM"

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT_NUM" --workers 1 --log-level info
```

## Current Configuration

### railway.toml
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

# Let Railway handle startup automatically
# Railway will use the Dockerfile CMD by default

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 5
numReplicas = 1
```

### Dockerfile
```dockerfile
# Use Railway Python startup script
CMD ["python", "scripts/railway_start.py"]
```

## File Structure

```
aggregator/
├── start.sh                    # Shell startup script
├── start.py                    # Python startup script (enhanced)
├── scripts/
│   ├── railway_start.py        # Railway-specific Python script
│   ├── healthcheck.py          # Health check scripts
│   └── ...
├── Dockerfile                  # Container configuration
└── railway.toml               # Railway deployment config
```

## Alternative Approaches

### Option 1: Set PORT Explicitly in Railway Dashboard
1. Go to Railway dashboard
2. Navigate to your service
3. Go to Variables tab
4. Add `PORT=8000` (or any valid port number)

### Option 2: Use Railway's Default Behavior
Remove all custom startup scripts and let Railway use its default uvicorn detection.

### Option 3: Use Railway's Built-in Python Support
Railway has built-in support for Python applications. Try removing the Dockerfile and let Railway auto-detect the Python app.

## Testing Locally

### Test with PORT Environment Variable
```bash
# Test Railway Python script
PORT=8080 python scripts/railway_start.py

# Test shell script
PORT=8080 bash start.sh

# Test with no PORT
unset PORT && python scripts/railway_start.py
```

## Expected Behavior

### Successful Deployment
```
Starting Astral Aggregator...
Using port: 12345
Executing: /usr/local/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 12345 --workers 1
```

### Fallback Behavior
```
Starting Astral Aggregator...
Using port: 8000
Executing: /usr/local/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## Next Steps

1. **Deploy with Railway Python script** - This should resolve the PORT issue
2. **Monitor logs** - Look for "Using port:" messages
3. **If still failing** - Try setting PORT explicitly in Railway dashboard
4. **Consider Railway's auto-detection** - Remove Dockerfile and let Railway handle everything

## Railway-Specific Notes

- Railway automatically provides the `PORT` environment variable
- Railway prefers simple startup commands
- Railway has built-in Python support that can auto-detect FastAPI/uvicorn apps
- Railway's environment variable expansion should work automatically
- If environment variables aren't expanding, it's usually a startup script issue 