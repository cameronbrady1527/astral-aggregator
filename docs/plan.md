I'll help you organize this project and create a robust, scalable solution for website change detection. Let me first explore your current codebase structure to understand what we're working with.

Read file: main.py
Read file: app/main.py
Read file: pyproject.toml
Ran tool
Ran tool
Ran tool
Now let me search for any existing router files to understand the current structure:

Ran tool
Based on my analysis of your codebase and the requirements, here's my comprehensive plan for building a robust, scalable website change detection system:

## Project Architecture Overview

### 1. **Core Components Structure**

```
app/
├── crawler/
│   ├── __init__.py
│   ├── sitemap_detector.py      # Sitemap-based change detection
│   ├── firecrawl_detector.py    # Firecrawl-based change detection
│   ├── change_analyzer.py       # Core change detection logic
│   └── base_detector.py         # Abstract base class
├── db/
│   ├── __init__.py
│   ├── models.py                # Database models for tracking
│   ├── crud.py                  # Database operations
│   └── database.py              # Database connection
├── routers/
│   ├── __init__.py
│   ├── listeners.py             # API endpoints for listeners
│   └── health.py                # Health check endpoint
├── utils/
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   └── scheduler.py             # Task scheduling
└── main.py
```

### 2. **Configuration Management**

Create a `config.yaml` file for easy site management:

```yaml
# config/sites.yaml
sites:
  judiciary_uk:
    name: "Judiciary UK"
    url: "https://www.judiciary.uk/"
    sitemap_url: "https://www.judiciary.uk/sitemap_index.xml"
    detection_methods: ["sitemap", "firecrawl"]
    check_interval_minutes: 1440  # 24 hours
    
  waverley_gov:
    name: "Waverley Borough Council"
    url: "https://www.waverley.gov.uk/"
    sitemap_url: "https://www.waverley.gov.uk/sitemap.xml"
    detection_methods: ["sitemap", "firecrawl"]
    check_interval_minutes: 1440

firecrawl:
  api_key: "${FIRECRAWL_API_KEY}"
  base_url: "https://api.firecrawl.dev"

database:
  url: "sqlite:///./change_detection.db"
```
Note: Database is not implemented yet. This is simply a placeholder for future support.

### 3. **Implementation Plan**

#### Phase 1: Core Infrastructure

1. **Database Models** - Track site states and changes
2. **Base Detector Class** - Abstract interface for different detection methods
3. **Configuration System** - YAML-based site configuration
4. **Basic API Endpoints** - Manual trigger endpoints

#### Phase 2: Detection Methods

1. **Sitemap Detector** - Parse and compare sitemaps
2. **Firecrawl Detector** - Integration with Firecrawl API
3. **Change Analyzer** - Compare and identify differences

#### Phase 3: Scheduling & Automation

1. **Task Scheduler** - Automated periodic checks
2. **Webhook Support** - Real-time triggers
3. **Notification System** - Alert mechanisms

### 4. **Key Design Decisions**

#### **Robust Change Detection Strategy:**

1. **Multi-Method Approach**: Combine sitemap and Firecrawl for redundancy
2. **State Persistence**: Store previous states in database for comparison
3. **Configurable Intervals**: Different check frequencies per site
4. **Error Handling**: Graceful degradation when one method fails

#### **Scalability Considerations:**

1. **Modular Design**: Easy to add new detection methods
2. **Async Processing**: Non-blocking operations
3. **Database Indexing**: Efficient queries for large datasets
4. **Rate Limiting**: Respect site policies

### 5. **Implementation Details**

#### **Database Schema:**
```sql
-- Sites table
CREATE TABLE sites (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    sitemap_url TEXT,
    detection_methods TEXT,  -- JSON array
    check_interval_minutes INTEGER DEFAULT 1440,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Site states table
CREATE TABLE site_states (
    id INTEGER PRIMARY KEY,
    site_id INTEGER,
    detection_method TEXT,
    state_data TEXT,  -- JSON with URLs and metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES sites(id)
);

-- Changes table
CREATE TABLE changes (
    id INTEGER PRIMARY KEY,
    site_id INTEGER,
    detection_method TEXT,
    change_type TEXT,  -- 'new', 'modified', 'deleted'
    url TEXT,
    change_data TEXT,  -- JSON with details
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES sites(id)
);
```

#### **API Endpoints:**
```python
# Manual triggers
POST /api/listeners/trigger/{site_id}
POST /api/listeners/trigger/all

# Status and results
GET /api/listeners/status
GET /api/listeners/changes/{site_id}
GET /api/listeners/changes

# Configuration
GET /api/listeners/sites
POST /api/listeners/sites
PUT /api/listeners/sites/{site_id}
```

### 6. **Change Detection Logic**

#### **Sitemap Method:**
1. Fetch sitemap XML
2. Parse URLs and metadata (lastmod, changefreq)
3. Compare with previous state
4. Identify new URLs and modified timestamps

#### **Firecrawl Method:**
1. Use Firecrawl's change tracking API
2. Compare with previous crawl results
3. Extract change status (new, modified, deleted)
4. Store detailed change information

### 7. **Output Format**

Following Firecrawl's format:
```json
{
  "site_id": "judiciary_uk",
  "detection_method": "firecrawl",
  "timestamp": "2024-01-15T10:30:00Z",
  "changes": [
    {
      "url": "https://www.judiciary.uk/new-page",
      "change_type": "new",
      "title": "New Judicial Guidance",
      "detected_at": "2024-01-15T10:30:00Z"
    },
    {
      "url": "https://www.judiciary.uk/existing-page",
      "change_type": "modified",
      "title": "Updated Content",
      "previous_hash": "abc123",
      "current_hash": "def456",
      "detected_at": "2024-01-15T10:30:00Z"
    }
  ],
  "summary": {
    "total_changes": 2,
    "new_pages": 1,
    "modified_pages": 1,
    "deleted_pages": 0
  }
}
```

### 8. **Next Steps**

1. **Start with database models** - Set up the foundation
2. **Implement sitemap detector** - Simpler to start with
3. **Add Firecrawl integration** - More sophisticated detection
4. **Create API endpoints** - Manual triggering
5. **Add scheduling** - Automated checks
6. **Implement notifications** - Alert system

Would you like me to start implementing any specific part of this plan? I'd recommend beginning with the database models and sitemap detector as they provide a solid foundation for the more complex Firecrawl integration.