# Astral API Test Suite

This directory contains comprehensive tests for the Astral API website change detection system.

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests for individual components
│   ├── test_config.py         # Configuration management tests
│   ├── test_base_detector.py  # Base detector class tests
│   └── test_json_writer.py    # JSON writer utility tests
├── api/                        # API endpoint tests
│   ├── test_main_endpoints.py # Main application endpoints
│   ├── test_listeners.py      # Listeners router endpoints
│   └── test_dashboard.py      # Dashboard router endpoints
└── integration/               # Integration tests
    └── test_change_detection.py # Complete workflow tests
```

## Running Tests

### Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install pytest pytest-asyncio httpx
```

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Running Specific Test Categories

```bash
# Run only unit tests
pytest tests/unit/

# Run only API tests
pytest tests/api/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_config.py
```

### Running Tests with Different Options

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run tests and stop on first failure
pytest -x

# Run tests and show local variables on failure
pytest -l

# Run tests with detailed output
pytest -s
```

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation:

- **Configuration Management**: Tests for `SiteConfig` and `ConfigManager` classes
- **Base Detector**: Tests for `ChangeResult` and `BaseDetector` classes
- **JSON Writer**: Tests for file writing and data serialization

### API Tests (`tests/api/`)

Test FastAPI endpoints and HTTP responses:

- **Main Endpoints**: Health checks, debug info, and basic functionality
- **Listeners API**: Change detection triggers and status endpoints
- **Dashboard**: HTML responses and frontend functionality

### Integration Tests (`tests/integration/`)

Test complete workflows and component interactions:

- **Change Detection Workflow**: End-to-end testing from config to output
- **Multiple Sites**: Testing detection across multiple configured sites
- **Error Handling**: Testing system behavior under failure conditions

## Test Configuration

### Fixtures

The `conftest.py` file provides shared fixtures:

- `test_config`: Sample configuration data
- `temp_config_file`: Temporary YAML configuration file
- `temp_output_dir`: Temporary output directory
- `client`: FastAPI test client
- `mock_*`: Various mock objects for testing

### Environment Setup

Tests automatically set up a test environment:

- Sets `TESTING=true` environment variable
- Uses temporary files and directories
- Mocks external dependencies (HTTP requests, file system)

## Writing New Tests

### Unit Test Example

```python
def test_site_config_initialization():
    """Test SiteConfig initialization with basic parameters."""
    config = SiteConfig(
        name="Test Site",
        url="https://test.example.com/",
        sitemap_url="https://test.example.com/sitemap.xml"
    )
    
    assert config.name == "Test Site"
    assert config.url == "https://test.example.com/"
    assert config.detection_methods == ["sitemap"]
```

### API Test Example

```python
def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] in ["healthy", "initializing"]
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_complete_workflow(temp_config_file, temp_output_dir):
    """Test the complete change detection workflow."""
    config_manager = ConfigManager(temp_config_file)
    json_writer = JSONWriter(temp_output_dir)
    
    # Test implementation...
    assert result.detection_method == "sitemap"
    assert len(result.changes) == 2
```

## Test Best Practices

1. **Use Descriptive Names**: Test function names should clearly describe what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification phases
3. **Mock External Dependencies**: Avoid making real HTTP requests or file system operations
4. **Test Edge Cases**: Include tests for error conditions and boundary values
5. **Keep Tests Independent**: Each test should be able to run in isolation
6. **Use Fixtures**: Leverage pytest fixtures for common setup and teardown

## Coverage Goals

The test suite aims for comprehensive coverage:

- **Unit Tests**: 90%+ coverage of core business logic
- **API Tests**: 100% coverage of all endpoints
- **Integration Tests**: Key workflow scenarios and error conditions

## Continuous Integration

Tests are automatically run in CI/CD pipelines:

- All tests must pass before deployment
- Coverage reports are generated and tracked
- Performance benchmarks are monitored

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the app module is in your Python path
2. **Async Test Failures**: Use `@pytest.mark.asyncio` for async tests
3. **Mock Issues**: Verify mock objects are properly configured
4. **File Permission Errors**: Tests use temporary directories to avoid permission issues

### Debug Mode

Run tests with debug output:

```bash
pytest -s -v --tb=long
```

This will show:
- Detailed test output
- Full tracebacks on failures
- Print statements and logging 