# Scripts Directory

This directory contains deployment and utility scripts for the Astral Aggregator.

## Core Scripts

### Health Check Scripts
- **`healthcheck.py`** - Python-based health check for Docker containers
- **`healthcheck.sh`** - Bash-based health check fallback
- **`railway_healthcheck.py`** - Railway deployment health check

### Deployment Scripts
- **`start.py`** - Application startup script
- **`railway_start.py`** - Railway deployment startup

## Feature Scripts

### Baseline Management
- **`create_comprehensive_baseline.py`** - Create comprehensive site baselines
- **`daily_baseline_system.py`** - Automated daily baseline system
- **`manage_baselines.py`** - Baseline management utilities

### Monitoring & Export
- **`automated_monitor.py`** - Automated monitoring system
- **`export_changes_to_excel.py`** - Export change detection data to Excel
- **`export_changes_cli.py`** - Command-line interface for exports
- **`README_EXPORT.md`** - Export functionality documentation

## Usage

### Health Checks
```bash
# Docker health check
python scripts/healthcheck.py

# Bash health check
./scripts/healthcheck.sh

# Railway health check
python scripts/railway_healthcheck.py
```

### Application Startup
```bash
# Local startup
python scripts/start.py

# Railway startup
python scripts/railway_start.py
```

### Baseline Management
```bash
# Create comprehensive baseline
python scripts/create_comprehensive_baseline.py

# Run daily baseline system
python scripts/daily_baseline_system.py

# Manage baselines
python scripts/manage_baselines.py
```

### Export Changes
```bash
# Export to Excel
python scripts/export_changes_to_excel.py

# CLI export with options
python scripts/export_changes_cli.py --help
```

### Automated Monitoring
```bash
# Run automated monitor
python scripts/automated_monitor.py
```

## Docker Integration

Health check scripts are automatically used by the Dockerfile:

```dockerfile
# Health check with more lenient settings using Python script
HEALTHCHECK --interval=90s --timeout=30s --start-period=300s --retries=3 \
    CMD python scripts/healthcheck.py
```

## Railway Integration

Railway uses its own built-in health check against the `/ping` endpoint, but these scripts provide additional monitoring for Docker deployments.

## Troubleshooting

If health checks are failing:

1. **Check the logs** for detailed error messages
2. **Verify the app is running** on the correct port
3. **Test endpoints manually** using curl or a web browser
4. **Check environment variables** especially `PORT`

## Local Testing

For local testing of health endpoints, use the test script in the `tests/` directory:

```bash
python tests/test_healthcheck.py
``` 