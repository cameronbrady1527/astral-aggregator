# Setup Guide

## Environment Variables

### Required Environment Variables

1. **FIRECRAWL_API_KEY** - Your Firecrawl API key
   - Get your API key from [Firecrawl](https://firecrawl.dev)
   - Set this in your Railway environment variables

### Local Development Setup

1. Copy the example configuration files:
   ```bash
   cp config/sites.yaml.example config/sites.yaml
   cp config/sites_railway.yaml.example config/sites_railway.yaml
   ```

2. Set your environment variables:
   ```bash
   # Windows PowerShell
   $env:FIRECRAWL_API_KEY="your-api-key-here"
   
   # Linux/Mac
   export FIRECRAWL_API_KEY="your-api-key-here"
   ```

3. Or create a `.env` file in the root directory:
   ```
   FIRECRAWL_API_KEY=your-api-key-here
   ```

### Railway Deployment Setup

1. In your Railway project dashboard, go to the "Variables" tab
2. Add the following environment variable:
   - **FIRECRAWL_API_KEY** = `your-api-key-here`

### Security Notes

- Never commit API keys to version control
- The config files with API keys are in `.gitignore`
- Always use environment variables for sensitive data
- Example files are provided without actual API keys

## Configuration Files

- `config/sites.yaml` - Main configuration (local development)
- `config/sites_railway.yaml` - Railway-optimized configuration
- Both files use `${FIRECRAWL_API_KEY}` placeholder for the API key

## Testing

After setting up your API key, test the application:

```bash
# Local development
uv run python scripts/start.py

# Test Railway configuration locally
$env:RAILWAY_ENVIRONMENT="production"; $env:CONFIG_FILE="config/sites_railway.yaml"; uv run python scripts/start.py
``` 