# Test Suite Documentation

## Overview

This test suite provides comprehensive testing for the aggregator project using pytest. The tests are organized into different categories and use modern Python testing practices.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures and configuration
├── test_basic.py              # Basic functionality tests
├── unit/                      # Unit tests
│   ├── __init__.py
│   ├── test_config.py         # Configuration management tests
│   └── test_sitemap_detector.py # Sitemap detector tests
├── integration/               # Integration tests
│   ├── __init__.py
│   └── test_change_detection.py # End-to-end change detection tests
└── api/                       # API tests
    ├── __init__.py
    └── test_listeners.py      # FastAPI endpoint tests
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, classes, or modules
- **Speed**: Fast execution
- **Dependencies**: Mocked external dependencies

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and workflows
- **Scope**: Multiple components working together
- **Speed**: Medium execution time
- **Dependencies**: Some real dependencies, mocked external services

### API Tests (`tests/api/`)
- **Purpose**: Test FastAPI endpoints and HTTP responses
- **Scope**: API contract and response validation
- **Speed**: Fast execution
- **Dependencies**: Mocked backend services

## Running Tests

### Basic Commands

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run specific test function
uv run pytest tests/unit/test_config.py::test_config_manager_initialization
```

### Using the Test Runner Script

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --type unit

# Run integration tests with coverage
python run_tests.py --type integration --coverage

# Run API tests with verbose output
python run_tests.py --type api --verbose

# Skip slow tests
python run_tests.py --fast

# Show available test markers
python run_tests.py --markers
```

### Test Markers

The test suite uses pytest markers to categorize tests:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.asyncio` - Async tests

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"

# Run async tests only
uv run pytest -m asyncio
```

## Test Configuration

### pytest Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
```

### Coverage Configuration

- **Source**: `app/` directory
- **Reports**: Terminal, HTML, and XML formats
- **Exclusions**: Test files, migrations, cache directories

## Shared Fixtures

### Core Fixtures (`conftest.py`)

- `test_config` - Test configuration settings
- `temp_output_dir` - Temporary output directory
- `mock_sitemap_xml` - Sample sitemap XML
- `mock_sitemap_index_xml` - Sample sitemap index XML
- `mock_aiohttp_session` - Mocked aiohttp session
- `mock_firecrawl_app` - Mocked Firecrawl app
- `sample_site_config` - Sample site configuration
- `sample_change_result` - Sample change detection result

### Usage Example

```python
def test_with_fixtures(sample_site_config, mock_sitemap_xml):
    """Test using shared fixtures."""
    assert sample_site_config["name"] == "Test Site"
    assert "urlset" in mock_sitemap_xml
```

## Mocking Strategy

### HTTP Requests
- **Tool**: `aioresponses` for async HTTP mocking
- **Scope**: All external HTTP calls
- **Benefits**: Fast, reliable, no network dependencies

### External Services
- **Tool**: `unittest.mock` and `pytest-mock`
- **Scope**: Firecrawl API, file system operations
- **Benefits**: Controlled test environment

### Example Mocking

```python
@patch('aiohttp.ClientSession.get')
async def test_http_request(mock_get):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.text = asyncio.coroutine(lambda: "<xml>...</xml>")
    mock_get.return_value.__aenter__.return_value = mock_response
    
    # Test code here
```

## Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### Async Testing
- Use `@pytest.mark.asyncio` for async tests
- Mock async dependencies properly
- Handle async context managers

### Error Testing
- Test both success and failure scenarios
- Verify error messages and status codes
- Test edge cases and boundary conditions

### Performance
- Keep unit tests fast (< 100ms each)
- Use appropriate markers for slow tests
- Mock expensive operations

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: |
          pip install uv
          uv sync --extra test
          uv run pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `app/` is in Python path
2. **Async Test Failures**: Check `@pytest.mark.asyncio` decorators
3. **Mock Issues**: Verify mock setup and teardown
4. **Coverage Issues**: Check source paths in coverage config

### Debug Mode

```bash
# Run with debug output
uv run pytest -v -s --tb=long

# Run single test with debug
uv run pytest tests/unit/test_config.py::test_config_manager_initialization -v -s
```

## Adding New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import patch, MagicMock

from app.module import ClassToTest

class TestClassToTest:
    """Test cases for ClassToTest."""
    
    def test_method_name(self):
        """Test description."""
        # Arrange
        instance = ClassToTest()
        
        # Act
        result = instance.method()
        
        # Assert
        assert result == expected_value
```

### Integration Test Template

```python
import pytest
from unittest.mock import patch

class TestFeatureIntegration:
    """Integration tests for feature."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_feature_workflow(self, mock_dependency):
        """Test complete feature workflow."""
        # Test implementation
        pass
```

### API Test Template

```python
import pytest
from fastapi.testclient import TestClient

class TestAPIEndpoint:
    """API tests for endpoint."""
    
    def test_endpoint_success(self, client, mock_service):
        """Test successful API call."""
        response = client.get("/api/endpoint")
        assert response.status_code == 200
```

## Coverage Goals

- **Unit Tests**: > 90% line coverage
- **Integration Tests**: > 80% line coverage
- **API Tests**: > 95% endpoint coverage
- **Overall**: > 85% total coverage

## Performance Benchmarks

- **Unit Tests**: < 5 seconds total
- **Integration Tests**: < 30 seconds total
- **API Tests**: < 10 seconds total
- **Full Suite**: < 45 seconds total 