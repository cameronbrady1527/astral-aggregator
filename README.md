# Astral API - Website Change Detection System

A robust, scalable system for monitoring website changes using multiple detection methods. Currently supports sitemap-based detection and Firecrawl API integration.

## Features

- **Multi-Method Detection**: Compare sitemap-based and Firecrawl-based change detection
- **Web Dashboard**: Interactive dashboard for monitoring changes and system status
- **JSON File Storage**: Simple file-based storage for easy development and testing
- **Configurable Sites**: YAML-based configuration for easy site management
- **REST API**: FastAPI endpoints for triggering and monitoring detection
- **Scalable Architecture**: Easy to add new detection methods and sites
- **Docker Support**: Containerized deployment with health checks
- **Railway Deployment**: Optimized for Railway cloud platform
- **Comprehensive Testing**: Unit, integration, and API tests with coverage

## Quick Start

### 1. Install Dependencies

This project uses `uv` for dependency management (recommended), but you can use any Python package manager you prefer.

**Option 1: Using uv (Recommended)**
```bash
# Install uv if you don't have it

# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On Windows (with winget):
winget install --id=astral-sh.uv

# On Windows (with chocolatey):
choco install uv

# Install dependencies
uv sync
```

**Option 2: Using pip**
```bash
# Install Python dependencies
pip install -e .
```

**Option 3: Using poetry**
```bash
# Install dependencies
poetry install
```

**Note**: This project includes a `uv.lock` file for reproducible builds. If you're using a different package manager, you can safely ignore this file - it won't affect your installation.

### 2. Configuration

1. **Copy the example configuration:**
   ```bash
   cp config/sites.yaml.example config/sites.yaml
   ```

2. **Update the configuration:**
   - Add your Firecrawl API key
   - Modify site URLs and settings as needed
   - The system comes pre-configured with these sites:
     - **Judiciary UK**: https://www.judiciary.uk/
     - **Waverley Borough Council**: https://www.waverley.gov.uk/

You can modify this file to add more sites or change settings.

**Note**: The `config/sites.yaml` file contains sensitive API keys and is not tracked in git. Always use the example file as a template.

### 3. Run the API Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Access the Dashboard

Once the server is running, you can access the interactive dashboard at:

```
http://localhost:8000/dashboard/
```

The dashboard provides:
- Real-time system status and statistics
- Visual charts showing change detection results
- Quick action buttons for triggering detection
- Site-specific monitoring views
- Historical change data visualization

### 5. Test the System

Run the comprehensive test suite to ensure everything is working correctly:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/      # Unit tests only
pytest tests/api/       # API tests only
pytest tests/integration/ # Integration tests only
```

## API Usage

### Core Endpoints

#### Health and Status
```bash
# Check system health
curl http://localhost:8000/health

# Simple ping
curl http://localhost:8000/ping

# Debug information
curl http://localhost:8000/debug
```

#### Change Detection
```bash
# Trigger detection for a specific site
curl -X POST http://localhost:8000/api/listeners/trigger/test_site

# Trigger detection for all sites
curl -X POST http://localhost:8000/api/listeners/trigger/all

# Get system status
curl http://localhost:8000/api/listeners/status

# Get list of configured sites
curl http://localhost:8000/api/listeners/sites
```

#### Analytics and History
```bash
# Get system analytics
curl http://localhost:8000/api/listeners/analytics

# Get site-specific analytics
curl http://localhost:8000/api/listeners/analytics/test_site

# Get recent changes
curl http://localhost:8000/api/listeners/changes

# Get historical data
curl http://localhost:8000/api/listeners/history?days=7
```

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Testing

### Running Tests

The project includes a comprehensive test suite covering unit tests, API tests, and integration tests.

#### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx
```

#### Test Commands
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/api/            # API tests  
pytest tests/integration/    # Integration tests

# Run specific test file
pytest tests/unit/test_config.py

# Run tests in parallel
pytest -n auto

# Run tests and stop on first failure
pytest -x
```

#### Test Categories

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **API Tests** (`tests/api/`): Test FastAPI endpoints and HTTP responses
- **Integration Tests** (`tests/integration/`): Test complete workflows

#### Coverage Goals

- **Unit Tests**: 90%+ coverage of core business logic
- **API Tests**: 100% coverage of all endpoints
- **Integration Tests**: Key workflow scenarios and error conditions

For detailed testing information, see [tests/README.md](tests/README.md).

## Configuration

### Site Configuration

Sites are configured in `config/sites.yaml`:

```yaml
sites:
  site_id:
    name: "Site Name"
    url: "https://example.com/"
    sitemap_url: "https://example.com/sitemap.xml"
    detection_methods: ["sitemap", "firecrawl"]
    check_interval_minutes: 1440
    is_active: true
```

### Environment Variables

- `CONFIG_FILE`: Path to configuration file (default: `config/sites.yaml`)
- `PORT`: Server port (default: 8000)
- `RAILWAY_ENVIRONMENT`: Set to enable Railway-specific configuration

### Firecrawl Configuration

```yaml
firecrawl:
  api_key: "your-api-key"
  base_url: "https://api.firecrawl.dev"
```

### Tor Proxy Configuration

The system supports Tor for anonymous web scraping. Tor provides free, anonymous access and is automatically managed by the application.

#### Automatic Setup

The application automatically handles Tor setup and management:

1. **Install Tor or Tor Browser:**
   - **Windows**: Download [Tor Browser](https://www.torproject.org/download/) or standalone Tor
   - **macOS**: `brew install tor` or download Tor Browser
   - **Linux**: `sudo apt install tor` (Ubuntu/Debian) or download Tor Browser

2. **Enable Tor in your environment:**
   ```bash
   export PROXY_PROVIDER=tor
   ```

3. **Start the application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

The application will automatically:
- ✅ Detect Tor installation (standalone or Tor Browser)
- ✅ Create Tor configuration files
- ✅ Start Tor service on startup
- ✅ Manage Tor lifecycle (start/stop/restart)
- ✅ Handle Tor health monitoring
- ✅ Clean up Tor processes on shutdown

#### Configuration Options

```yaml
# In your site configuration
sites:
  site_id:
    name: "Site Name"
    url: "https://example.com/"
    proxy_enabled: true
    proxy_provider: "tor"
    proxy_timeout: 30
```

#### Features

- **Automatic Management**: Tor is started/stopped with the application
- **Health Monitoring**: Automatic health checks and restart on failure
- **IP Rotation**: Tor automatically rotates IP addresses every 10 requests
- **Circuit Management**: Automatic circuit management for better performance
- **Anonymous Browsing**: All requests go through the Tor network
- **Graceful Shutdown**: Proper cleanup of Tor processes

#### Performance Considerations

- Tor is significantly slower than commercial proxies (2-10x slower)
- Connection timeouts should be increased (30+ seconds recommended)
- Concurrent requests are limited by Tor circuit capacity
- Consider using multiple Tor instances for high-volume scraping

#### Testing

Test the Tor integration:
```bash
python test_tor_integration.py
```

## Development

### Project Structure

```
aggregator/
├── app/                    # Main application code
│   ├── main.py            # FastAPI application entry point
│   ├── routers/           # API route handlers
│   ├── crawler/           # Change detection logic
│   ├── utils/             # Utility functions
│   └── db/                # Database models (if applicable)
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── api/               # API tests
│   └── integration/       # Integration tests
├── config/                # Configuration files
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

### Adding New Detection Methods

1. Create a new detector class in `app/crawler/`
2. Inherit from `BaseDetector`
3. Implement required methods
4. Add to site configuration
5. Update tests

### Adding New Sites

1. Add site configuration to `config/sites.yaml`
2. Test with the API endpoints
3. Verify detection works correctly

## Deployment

### Docker Deployment

```bash
# Build the image
docker build -t astral-api .

# Run the container
docker run -p 8000:8000 astral-api
```

### Railway Deployment

The project is optimized for Railway deployment:

1. Connect your repository to Railway
2. Set environment variables
3. Deploy automatically

### Health Checks

The application includes health check endpoints:
- `/health` - System health status
- `/ping` - Simple connectivity test

## Troubleshooting

### Common Issues

1. **Configuration Errors**: Ensure `config/sites.yaml` exists and is valid YAML
2. **API Key Issues**: Verify Firecrawl API key is correct and has sufficient credits
3. **Port Conflicts**: Change the port if 8000 is already in use
4. **Import Errors**: Ensure all dependencies are installed

### Debug Mode

Enable debug output:
```bash
# Set debug environment variable
export DEBUG=true

# Run with debug logging
uvicorn app.main:app --reload --log-level debug
```

### Logs

Check application logs for detailed error information:
```bash
# View logs in real-time
tail -f logs/app.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd aggregator

# Install dependencies
uv sync

# Run tests
pytest

# Start development server
uvicorn app.main:app --reload
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the documentation in `docs/`
- Review the test examples in `tests/`
- Open an issue on GitHub
