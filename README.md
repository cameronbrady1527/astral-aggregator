# Website Change Detection System

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

**Option 1: Test via API (Recommended)**
```bash
# Check system status (works in browser)
curl "http://localhost:8000/api/listeners/status"

# Trigger change detection for Judiciary UK
curl -X POST "http://localhost:8000/api/listeners/trigger/judiciary_uk"

# View recent changes
curl "http://localhost:8000/api/listeners/changes/judiciary_uk"
```

**Option 2: Run test scripts**
```bash
# Run the test script
python tests/test_change_detection.py

# Or use the test runner
python run_tests.py

# Run with coverage
python run_tests.py --coverage
```

**Option 3: Interactive API Documentation**
Visit `http://localhost:8000/docs` in your browser for interactive API testing.

## Project Structure

```
aggregator/
├── app/                    # Main application code
│   ├── crawler/           # Change detection modules
│   ├── db/                # Database models and operations
│   ├── routers/           # FastAPI route handlers
│   │   ├── dashboard.py   # Web dashboard endpoints
│   │   ├── listeners.py   # Change detection API
│   │   ├── users.py       # User management (placeholder)
│   │   └── items.py       # Item management (placeholder)
│   └── utils/             # Utility functions
├── config/                # Configuration files
│   ├── sites.yaml         # Site configuration (not in git)
│   ├── sites.yaml.example # Example configuration
│   └── sites_railway.yaml.example # Railway-specific config
├── docs/                  # Documentation
│   ├── deploy.md          # Deployment guide
│   ├── plan.md            # Project planning
│   ├── SETUP.md           # Setup instructions
│   └── README.md          # Documentation overview
├── scripts/               # Deployment and utility scripts
│   ├── healthcheck.py     # Python health check script
│   ├── healthcheck.sh     # Bash health check script
│   ├── railway_start.py   # Railway startup script
│   ├── start.py           # Local startup script
│   ├── diagnose.py        # System diagnostics
│   ├── deploy_debug.py    # Deployment debugging
│   └── README.md          # Scripts documentation
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── api/              # API tests
│   ├── test_healthcheck.py # Local health check testing
│   └── README.md         # Testing documentation
├── output/               # Generated output (not in git)
├── Dockerfile            # Container configuration
├── railway.toml          # Railway deployment config
├── pyproject.toml        # Project metadata and dependencies
├── requirements.txt      # Python dependencies
└── run_tests.py          # Test runner script
```

## API Endpoints

### Health Check & Documentation
```bash
# Health check (works in browser)
curl "http://localhost:8000/"

# Interactive API documentation (works in browser)
# Visit: http://localhost:8000/docs
```

### Dashboard
```bash
# Web dashboard (works in browser)
# Visit: http://localhost:8000/dashboard/
```

### Trigger Change Detection (POST requests only)

**Important**: These endpoints require POST requests, not GET requests.

```bash
# Detect changes for a specific site
curl -X POST "http://localhost:8000/api/listeners/trigger/judiciary_uk"

# Detect changes for Waverley Council
curl -X POST "http://localhost:8000/api/listeners/trigger/waverley_gov"

# Detect changes for all sites
curl -X POST "http://localhost:8000/api/listeners/trigger/all"
```

**Using PowerShell:**
```powershell
# Trigger detection for Judiciary UK
Invoke-RestMethod -Uri "http://localhost:8000/api/listeners/trigger/judiciary_uk" -Method POST

# Trigger detection for all sites
Invoke-RestMethod -Uri "http://localhost:8000/api/listeners/trigger/all" -Method POST
```

### View Status and Results (GET requests - work in browser)

```bash
# Get system status
curl "http://localhost:8000/api/listeners/status"

# List all sites
curl "http://localhost:8000/api/listeners/sites"

# Get site status
curl "http://localhost:8000/api/listeners/sites/judiciary_uk"

# Get recent changes for a site
curl "http://localhost:8000/api/listeners/changes/judiciary_uk"

# Get all recent changes
curl "http://localhost:8000/api/listeners/changes"
```

### Helpful Information Endpoints (GET requests - work in browser)

These endpoints provide guidance and information about using the API:

```bash
# Main API overview
curl "http://localhost:8000/"

# Listeners API overview with all endpoints
curl "http://localhost:8000/api/listeners/"

# Trigger instructions and examples
curl "http://localhost:8000/api/listeners/trigger"

# Site-specific trigger information
curl "http://localhost:8000/api/listeners/trigger/judiciary_uk"
```

**Browser-friendly URLs:**
- Main API info: `http://localhost:8000/`
- Dashboard: `http://localhost:8000/dashboard/`
- Listeners API overview: `http://localhost:8000/api/listeners/`
- Trigger instructions: `http://localhost:8000/api/listeners/trigger`
- Site-specific trigger info: `http://localhost:8000/api/listeners/trigger/judiciary_uk`
- System status: `http://localhost:8000/api/listeners/status`
- All sites: `http://localhost:8000/api/listeners/sites`
- Judiciary UK status: `http://localhost:8000/api/listeners/sites/judiciary_uk`
- Judiciary UK changes: `http://localhost:8000/api/listeners/changes/judiciary_uk`
- All changes: `http://localhost:8000/api/listeners/changes`
- Interactive API docs: `http://localhost:8000/docs`

## Configuration

### Site Configuration

Edit `config/sites.yaml` to configure sites:

```yaml
sites:
  judiciary_uk:
    name: "Judiciary UK"
    url: "https://www.judiciary.uk/"
    sitemap_url: "https://www.judiciary.uk/sitemap.xml"
    detection_methods: ["sitemap", "firecrawl"]
    check_interval_minutes: 1440  # 24 hours
    is_active: true
```

### Adding New Sites

1. Add a new entry to the `sites` section in `config/sites.yaml`
2. Set the `sitemap_url` (or let the system guess it)
   - For single sitemaps: `https://example.com/sitemap.xml`
   - For sitemap indexes: `https://example.com/sitemap_index.xml`
3. Choose detection methods: `["sitemap"]`, `["firecrawl"]`, or `["sitemap", "firecrawl"]`
4. Set the check interval in minutes

**Note**: The system automatically detects whether a URL points to a single sitemap or a sitemap index and handles both cases appropriately.

### Firecrawl Configuration

**Note:** Firecrawl detection requires a paid API plan with sufficient credits. The free tier may have limitations.

To use Firecrawl detection, add your API key to the configuration:

```yaml
firecrawl:
  api_key: "your_firecrawl_api_key_here"
  base_url: "https://api.firecrawl.dev"
```

**Important:** If you see "Payment Required: Insufficient credits" errors, you can:
1. Upgrade your Firecrawl plan at https://firecrawl.dev/pricing
2. Use only sitemap detection by setting `detection_methods: ["sitemap"]`
3. The sitemap detection works perfectly without requiring any API keys

## Deployment

### Docker Deployment

The project includes a Dockerfile for containerized deployment:

```bash
# Build the Docker image
docker build -t astral-aggregator .

# Run the container
docker run -p 8000:8000 astral-aggregator

# Run with custom configuration
docker run -p 8000:8000 -v $(pwd)/config:/app/config astral-aggregator
```

### Railway Deployment

The project is optimized for Railway deployment with:

- `railway.toml` configuration
- Railway-specific startup scripts
- Health check endpoints
- Environment-specific configurations

**Deployment Steps:**
1. Connect your repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy using Railway's automatic deployment

### Local Development

For development, you can use any of the installation methods above. If you're using `uv`, you can also run:

```bash
# Install in development mode
uv sync --dev

# Run the server with auto-reload
uv run uvicorn app.main:app --reload
```

## Testing

### Test Structure

The project includes comprehensive testing with pytest:

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for workflows
├── api/              # API endpoint tests
└── test_healthcheck.py # Health check testing
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test categories
uv run pytest tests/unit/           # Unit tests only
uv run pytest tests/integration/    # Integration tests only
uv run pytest tests/api/            # API tests only

# Run with the test runner script
python run_tests.py
python run_tests.py --coverage
python run_tests.py --type unit
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows
- **API Tests**: Test FastAPI endpoints and HTTP responses

## Output Format

### Change Detection Results

Results are stored in timestamped folders within the `output/` directory. Each run creates a new folder with the format `YYYYMMDD_HHMMSS` containing all JSON files for that execution:

```
output/
├── 20250730_154609/                    # Run timestamp
│   ├── Judiciary UK_20250730_154609.json
│   ├── Judiciary UK_state_20250730_154609.json
│   ├── Waverley Borough Council_20250730_154611.json
│   └── Waverley Borough Council_state_20250730_154611.json
├── 20250730_154611/                    # Another run
│   ├── Judiciary UK_20250730_154612.json
│   └── ...
└── ...
```

Each JSON file has the following structure:

```json
{
  "metadata": {
    "site_name": "Judiciary UK",
    "detection_time": "2024-01-15T10:30:00Z",
    "detection_method": "sitemap",
    "file_created": "2024-01-15T10:30:00Z",
    "run_timestamp": "20250730_154609"
  },
  "changes": {
    "site_id": "judiciary_uk",
    "site_name": "Judiciary UK",
    "detection_time": "2024-01-15T10:30:00Z",
    "methods": {
      "sitemap": {
        "detection_method": "sitemap",
        "site_name": "Judiciary UK",
        "detection_time": "2024-01-15T10:30:00Z",
        "changes": [
          {
            "url": "https://www.judiciary.uk/new-page",
            "change_type": "new",
            "detected_at": "2024-01-15T10:30:00Z",
            "title": "New page: https://www.judiciary.uk/new-page"
          }
        ],
        "summary": {
          "total_changes": 1,
          "new_pages": 1,
          "modified_pages": 0,
          "deleted_pages": 0
        },
                 "metadata": {
           "current_urls": 150,
           "previous_urls": 149,
           "new_urls": 1,
           "deleted_urls": 0,
           "sitemap_url": "https://www.judiciary.uk/sitemap_index.xml",
           "sitemap_info": {
             "type": "sitemap_index",
             "total_sitemaps": 23,
             "total_urls": 19255,
             "sitemaps": [
               {
                 "url": "https://www.judiciary.uk/post-sitemap.xml",
                 "status": "success",
                 "urls": 507,
                 "last_modified": "2025-07-25T16:31:23+00:00"
               }
             ]
           }
         }
      }
    }
  }
}
```

## Detection Methods

### Sitemap Detection

- **Pros**: Fast, lightweight, good for detecting new pages, supports sitemap indexes
- **Cons**: Only detects new/deleted pages, not content changes
- **Use Case**: Initial baseline and new page detection
- **Features**: 
  - Supports single sitemaps and sitemap indexes
  - Handles multiple sitemaps per site (e.g., posts, pages, judgments)
  - Parallel processing of individual sitemaps for performance

### Firecrawl Detection

- **Pros**: Sophisticated change detection, content analysis
- **Cons**: Requires API key, slower, more expensive
- **Use Case**: Detailed change analysis and content monitoring

## File Structure

```
aggregator/
├── app/
│   ├── crawler/
│   │   ├── base_detector.py      # Abstract base class
│   │   ├── sitemap_detector.py   # Sitemap-based detection
│   │   ├── firecrawl_detector.py # Firecrawl API integration
│   │   └── change_detector.py    # Main orchestrator
│   ├── routers/
│   │   ├── dashboard.py          # Web dashboard endpoints
│   │   └── listeners.py          # API endpoints
│   ├── utils/
│   │   ├── json_writer.py        # JSON file management
│   │   └── config.py             # Configuration management
│   └── main.py                   # FastAPI application
├── config/
│   └── sites.yaml                # Site configuration
├── output/                       # Timestamped run folders with JSON files
├── test_change_detection.py      # Test script
└── README.md
```

## Development

### Development Setup

For development, you can use any of the installation methods above. If you're using `uv`, you can also run:

```bash
# Install in development mode
uv sync --dev

# Run the server with auto-reload
uv run uvicorn app.main:app --reload
```

### Adding New Detection Methods

1. Create a new detector class that inherits from `BaseDetector`
2. Implement the required methods: `detect_changes()` and `get_current_state()`
3. Add the new method to the `_create_detector()` method in `ChangeDetector`
4. Update the configuration schema if needed

### Testing

```bash
# Run the test script
python test_change_detection.py

# Run specific tests
python -c "
import asyncio
from test_change_detection import test_sitemap_detection
asyncio.run(test_sitemap_detection())
"
```

## Scripts and Utilities

The `scripts/` directory contains various utility scripts:

- **`healthcheck.py`**: Python-based health check for Docker containers
- **`healthcheck.sh`**: Bash-based health check fallback
- **`railway_start.py`**: Railway-optimized startup script
- **`start.py`**: Local development startup script
- **`diagnose.py`**: System diagnostics and troubleshooting
- **`deploy_debug.py`**: Deployment debugging utilities

## Future Enhancements

- [ ] **Supabase Database Integration**: Replace file-based storage with Supabase PostgreSQL for scalable data management and real-time queries
- [ ] Scheduled detection using cron jobs
- [ ] Webhook notifications
- [ ] Email/Slack alerts
- [ ] Enhanced web interface for monitoring
- [ ] More detection methods (RSS feeds, API endpoints)
- [ ] Content diff visualization
- [ ] Historical change analysis
- [ ] User authentication and authorization
- [ ] Multi-tenant support

## Troubleshooting

### Common Issues

1. **"405 Method Not Allowed" errors**: 
   - Trigger endpoints require POST requests, not GET requests
   - Use `curl -X POST` or `Invoke-RestMethod -Method POST`
   - Visit the helpful GET endpoints for guidance: `/api/listeners/trigger`

2. **Sitemap not found**: Check if the sitemap URL is correct in the configuration
3. **Firecrawl API errors**: Verify your API key and check the Firecrawl documentation
4. **Permission errors**: Ensure the `output/` directory is writable
5. **Network timeouts**: Increase timeout values in the configuration
6. **Dashboard not loading**: Check if the dashboard router is properly loaded

### Logs

Check the console output for detailed error messages. The system provides comprehensive error reporting for debugging.

### Health Checks

The system includes multiple health check mechanisms:

- **Docker health checks**: Automatic container health monitoring
- **Railway health checks**: Platform-specific health monitoring
- **Manual health checks**: Use the scripts in the `scripts/` directory

## License

This project is licensed under the MIT License.
