# Baseline Evolution Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the baseline evolution system. The testing approach ensures that the system works correctly end-to-end, from individual components to complete workflows.

## Testing Philosophy

### 1. **Comprehensive Coverage**
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows
- **API Tests**: Test the system through its public interfaces
- **End-to-End Tests**: Test complete user scenarios
- **Performance Tests**: Ensure system performance under load

### 2. **Real Data Simulation**
- Use realistic test data that mimics production scenarios
- Simulate various change patterns (new URLs, deleted URLs, modified content)
- Test edge cases and error conditions

### 3. **Automated Validation**
- All tests are automated and can be run repeatedly
- Comprehensive reporting and failure analysis
- Performance benchmarking and regression detection

## Test Structure

### Unit Tests (`tests/unit/`)

#### `test_baseline_manager.py`
**Purpose**: Test baseline management functionality
**Coverage**:
- Baseline creation and saving
- Baseline retrieval and listing
- Baseline cleanup and maintenance
- Error handling and validation
- Concurrent access scenarios

**Key Test Scenarios**:
```python
def test_save_baseline(self):
    """Test saving a baseline to file."""
    
def test_get_latest_baseline_exists(self):
    """Test getting the latest baseline when it exists."""
    
def test_cleanup_old_baselines(self):
    """Test cleaning up old baselines."""
    
def test_concurrent_baseline_access(self):
    """Test concurrent access to baseline files."""
```

#### `test_baseline_merger.py`
**Purpose**: Test baseline merging logic
**Coverage**:
- Merging unchanged URLs from previous baseline
- Adding new URLs from current state
- Updating modified URLs with new hashes
- Removing deleted URLs
- Metadata consistency validation

**Key Test Scenarios**:
```python
def test_merge_baselines_complete(self):
    """Test complete baseline merging workflow."""
    
def test_merge_baselines_no_changes(self):
    """Test baseline merging when no changes detected."""
    
def test_validate_merge_result(self):
    """Test validation of merged baseline."""
```

### Integration Tests (`tests/integration/`)

#### `test_baseline_evolution_integration.py`
**Purpose**: Test complete baseline evolution workflows
**Coverage**:
- First detection creates initial baseline
- Baseline evolution with new URLs
- Baseline evolution with deleted URLs
- Baseline evolution with modified content
- Multiple consecutive evolutions
- Error handling scenarios
- Performance with large datasets

**Key Test Scenarios**:
```python
async def test_first_detection_creates_baseline(self):
    """Test that first detection creates initial baseline."""
    
async def test_baseline_evolution_mixed_changes(self):
    """Test baseline evolution with mixed changes."""
    
async def test_multiple_baseline_evolutions(self):
    """Test multiple consecutive baseline evolutions."""
    
async def test_baseline_evolution_performance(self):
    """Test baseline evolution performance with large datasets."""
```

### API Tests (`tests/api/`)

#### `test_baseline_evolution_api.py`
**Purpose**: Test baseline evolution through API endpoints
**Coverage**:
- Detection trigger with baseline evolution
- Baseline history and statistics endpoints
- Baseline rollback functionality
- Baseline validation endpoints
- Error handling in API responses

**Key Test Scenarios**:
```python
def test_trigger_site_detection_with_baseline_evolution(self, mock_get_detector, client):
    """Test that site detection trigger includes baseline evolution."""
    
def test_baseline_history_endpoint(self, mock_get_detector, client):
    """Test baseline history endpoint."""
    
def test_baseline_rollback_endpoint(self, mock_get_detector, client):
    """Test baseline rollback endpoint."""
```

## Test Data Strategy

### 1. **Realistic Test Data**
```python
# Sample baseline data structure
sample_baseline = {
    "site_id": "test_site",
    "site_name": "Test Site",
    "baseline_date": "20240101",
    "sitemap_state": {
        "urls": [
            "https://test.example.com/page1",
            "https://test.example.com/page2",
            "https://test.example.com/page3"
        ]
    },
    "content_hashes": {
        "https://test.example.com/page1": {"hash": "abc123", "content_length": 100},
        "https://test.example.com/page2": {"hash": "def456", "content_length": 200},
        "https://test.example.com/page3": {"hash": "ghi789", "content_length": 300}
    }
}
```

### 2. **Change Scenarios**
- **New URLs**: Add pages to sitemap
- **Deleted URLs**: Remove pages from sitemap
- **Modified Content**: Change content hashes
- **Mixed Changes**: Combination of all change types
- **No Changes**: Baseline remains the same

### 3. **Edge Cases**
- Empty baselines
- Corrupted data
- Large datasets (1000+ URLs)
- Concurrent operations
- Network failures

## Performance Testing

### 1. **Baseline Size Testing**
- Small baselines (1-10 URLs)
- Medium baselines (100-500 URLs)
- Large baselines (1000+ URLs)

### 2. **Change Volume Testing**
- Single changes
- Multiple changes (10-100)
- High-volume changes (1000+)

### 3. **Concurrent Operations**
- Multiple simultaneous detections
- Baseline updates during detection
- File system contention

### 4. **Performance Benchmarks**
```python
# Performance targets
PERFORMANCE_TARGETS = {
    "baseline_creation": "< 1 second for 100 URLs",
    "baseline_merging": "< 2 seconds for 1000 URLs",
    "change_detection": "< 5 seconds for 1000 URLs",
    "api_response": "< 500ms for status endpoints"
}
```

## Test Execution

### 1. **Individual Test Execution**
```bash
# Run specific test file
pytest tests/unit/test_baseline_manager.py -v

# Run specific test method
pytest tests/integration/test_baseline_evolution_integration.py::TestBaselineEvolutionWorkflow::test_first_detection_creates_baseline -v

# Run with coverage
pytest tests/unit/test_baseline_manager.py --cov=app.utils.baseline_manager --cov-report=html
```

### 2. **Comprehensive Test Suite**
```bash
# Run all baseline evolution tests
python scripts/run_baseline_evolution_tests.py

# Run specific test types
python scripts/run_baseline_evolution_tests.py --test-types unit integration

# Run with custom output
python scripts/run_baseline_evolution_tests.py --output custom_report.json
```

### 3. **Continuous Integration**
```yaml
# GitHub Actions example
- name: Run Baseline Evolution Tests
  run: |
    python scripts/run_baseline_evolution_tests.py --test-types unit integration api
    python scripts/run_baseline_evolution_tests.py --test-types e2e performance
```

## Test Reporting

### 1. **Test Results Structure**
```json
{
  "test_run": {
    "start_time": "2024-01-02T12:00:00",
    "end_time": "2024-01-02T12:05:00",
    "duration_seconds": 300.0
  },
  "summary": {
    "total_test_modules": 15,
    "total_passed_modules": 14,
    "total_failed_modules": 1,
    "overall_success_rate": 93.3
  },
  "results": {
    "unit_tests": {
      "total_modules": 5,
      "passed_modules": 5,
      "failed_modules": 0,
      "success_rate": 100.0
    },
    "integration_tests": {
      "total_modules": 3,
      "passed_modules": 2,
      "failed_modules": 1,
      "success_rate": 66.7
    }
  }
}
```

### 2. **Success Criteria**
- **Unit Tests**: > 95% success rate
- **Integration Tests**: > 90% success rate
- **API Tests**: > 90% success rate
- **End-to-End Tests**: > 85% success rate
- **Performance Tests**: All within time limits

## Error Handling Testing

### 1. **Expected Error Scenarios**
- Invalid baseline data
- Missing required fields
- Corrupted JSON files
- Network timeouts
- File system errors

### 2. **Error Recovery Testing**
- Graceful degradation
- Automatic retry mechanisms
- Fallback to previous state
- Error logging and reporting

### 3. **Error Validation**
```python
def test_error_handling_invalid_json(self):
    """Test error handling when reading invalid JSON files."""
    
def test_baseline_evolution_error_handling(self):
    """Test error handling during baseline evolution."""
```

## Validation Testing

### 1. **Data Integrity**
- Baseline structure validation
- URL consistency checks
- Hash integrity verification
- Metadata completeness

### 2. **Business Logic Validation**
- Correct change detection
- Proper baseline evolution
- No data loss during updates
- Consistent state across components

### 3. **API Contract Validation**
- Response format compliance
- Error code consistency
- Performance SLA adherence
- Backward compatibility

## Continuous Testing

### 1. **Automated Test Execution**
- Run on every code change
- Run on schedule (daily/weekly)
- Run before deployments
- Run in different environments

### 2. **Test Environment Management**
- Isolated test environments
- Clean baseline data
- Consistent test configurations
- Automated environment setup

### 3. **Test Data Management**
- Version-controlled test data
- Automated test data generation
- Test data cleanup
- Data anonymization for sensitive information

## Monitoring and Alerting

### 1. **Test Metrics**
- Test execution time
- Success/failure rates
- Performance regression detection
- Coverage trends

### 2. **Alerting Rules**
- Test failures in critical paths
- Performance degradation
- Coverage drops
- Environment issues

### 3. **Reporting**
- Daily test summaries
- Weekly trend analysis
- Monthly quality reports
- Release readiness assessments

## Best Practices

### 1. **Test Design**
- Write tests before implementation (TDD)
- Use descriptive test names
- Keep tests independent and isolated
- Use appropriate assertions

### 2. **Test Maintenance**
- Regular test review and updates
- Remove obsolete tests
- Update test data as needed
- Refactor tests for clarity

### 3. **Test Documentation**
- Document test scenarios
- Explain complex test logic
- Keep test data documentation updated
- Document test environment requirements

## Troubleshooting

### 1. **Common Issues**
- **Test Environment Issues**: Check dependencies and configurations
- **Data Consistency Issues**: Verify test data integrity
- **Performance Issues**: Monitor system resources
- **Timing Issues**: Add appropriate waits and timeouts

### 2. **Debugging Strategies**
- Use verbose test output
- Enable detailed logging
- Use test-specific debuggers
- Analyze test artifacts

### 3. **Recovery Procedures**
- Clean up test artifacts
- Reset test environment
- Restore baseline data
- Re-run failed tests

## Future Enhancements

### 1. **Test Automation**
- Automated test data generation
- Self-healing tests
- Intelligent test selection
- Parallel test execution

### 2. **Advanced Testing**
- Chaos engineering tests
- Security testing
- Load testing
- Stress testing

### 3. **Monitoring Integration**
- Real-time test monitoring
- Performance trend analysis
- Predictive failure detection
- Automated issue resolution

This comprehensive testing strategy ensures that the baseline evolution system is robust, reliable, and performs well under all conditions. Regular execution of these tests provides confidence in the system's functionality and helps identify issues early in the development cycle. 