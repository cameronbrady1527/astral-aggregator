# Website Change Detection System

A robust, scalable system for monitoring website changes using multiple detection methods. Currently supports sitemap-based detection and Firecrawl API integration.

## Features

- **Multi-Method Detection**: Compare sitemap-based and Firecrawl-based change detection
- **JSON File Storage**: Simple file-based storage for easy development and testing
- **Configurable Sites**: YAML-based configuration for easy site management
- **REST API**: FastAPI endpoints for triggering and monitoring detection
- **Scalable Architecture**: Easy to add new detection methods and sites

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -e .
```

### 2. Configuration

The system will automatically create a default configuration file at `config/sites.yaml` with the following sites:

- **Judiciary UK**: https://www.judiciary.uk/
- **Waverley Borough Council**: https://www.waverley.gov.uk/

You can modify this file to add more sites or change settings.

### 3. Run the API Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the System

```bash
# Run the test script
python test_change_detection.py
```

## API Endpoints

### Trigger Change Detection

```bash
# Detect changes for a specific site
curl -X POST "http://localhost:8000/api/listeners/trigger/judiciary_uk"

# Detect changes for all sites
curl -X POST "http://localhost:8000/api/listeners/trigger/all"
```

### View Status and Results

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
3. Choose detection methods: `["sitemap"]`, `["firecrawl"]`, or `["sitemap", "firecrawl"]`
4. Set the check interval in minutes

### Firecrawl Configuration

To use Firecrawl detection, add your API key to the configuration:

```yaml
firecrawl:
  api_key: "your_firecrawl_api_key_here"
  base_url: "https://api.firecrawl.dev"
```

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
          "sitemap_url": "https://www.judiciary.uk/sitemap.xml"
        }
      }
    }
  }
}
```

## Detection Methods

### Sitemap Detection

- **Pros**: Fast, lightweight, good for detecting new pages
- **Cons**: Only detects new/deleted pages, not content changes
- **Use Case**: Initial baseline and new page detection

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

## Future Enhancements

- [ ] **Supabase Database Integration**: Replace file-based storage with Supabase PostgreSQL for scalable data management and real-time queries
- [ ] Scheduled detection using cron jobs
- [ ] Webhook notifications
- [ ] Email/Slack alerts
- [ ] Web interface for monitoring
- [ ] More detection methods (RSS feeds, API endpoints)
- [ ] Content diff visualization
- [ ] Historical change analysis

## Troubleshooting

### Common Issues

1. **Sitemap not found**: Check if the sitemap URL is correct in the configuration
2. **Firecrawl API errors**: Verify your API key and check the Firecrawl documentation
3. **Permission errors**: Ensure the `output/` directory is writable
4. **Network timeouts**: Increase timeout values in the configuration

### Logs

Check the console output for detailed error messages. The system provides comprehensive error reporting for debugging.

## License

This project is licensed under the MIT License.
