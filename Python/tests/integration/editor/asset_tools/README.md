# Asset Management Tests

This directory contains comprehensive automated tests for all Unreal Engine asset management tools in the MCP system.

## Overview

The asset management test suite validates three main categories of asset operations:

1. **Core Asset Operations** (`test_asset_commands.py`)
   - load_asset, save_asset, duplicate_asset, delete_asset
   - rename_asset, move_asset, import_asset, export_asset

2. **Content Browser Operations** (`test_content_browser_commands.py`)
   - list_assets, get_asset_metadata, search_assets

3. **Asset Registry Operations** (`test_asset_registry_commands.py`)
   - get_asset_references, get_asset_dependencies

## Test Files

### Core Test Files
- `test_asset_commands.py` - Tests for core asset operations
- `test_content_browser_commands.py` - Tests for content browser functionality
- `test_asset_registry_commands.py` - Tests for asset registry operations

### Support Files
- `asset_test_utils.py` - Utilities for asset testing, cleanup, and validation
- `run_asset_tests.py` - Comprehensive test runner for all asset tests
- `README.md` - This documentation file

## Running Tests

### Run All Asset Tests
```bash
cd Python/tests/integration/editor/asset_tools
python run_asset_tests.py
```

### Run Individual Test Suites
```bash
# Core asset operations
python test_asset_commands.py

# Content browser operations  
python test_content_browser_commands.py

# Asset registry operations
python test_asset_registry_commands.py
```

### Test Runner Options
```bash
# Use mock server for offline testing
python run_asset_tests.py --mock

# Custom Unreal Engine connection
python run_asset_tests.py --host 192.168.1.100 --port 55557

# Save detailed results to file
python run_asset_tests.py --output asset_results.json

# Enable verbose logging
python run_asset_tests.py --verbose
```

## Test Configuration

Tests can be configured via environment variables or command-line arguments:

### Environment Variables
- `TEST_UNREAL_HOST` - Unreal Engine host (default: 127.0.0.1)
- `TEST_UNREAL_PORT` - Unreal Engine port (default: 55557) 
- `TEST_CONNECTION_TIMEOUT` - Connection timeout in seconds (default: 10)
- `TEST_COMMAND_TIMEOUT` - Command timeout in seconds (default: 30)
- `TEST_USE_MOCK` - Use mock server (default: false)

### Command Line Options
- `--host HOST` - Unreal Engine host address
- `--port PORT` - Unreal Engine port number
- `--mock` - Enable mock server mode
- `--timeout SECONDS` - Set command timeout
- `--output FILE` - Save results to JSON file
- `--verbose` - Enable detailed logging

## Test Categories

### Happy Path Tests
- Validate normal operation with valid inputs
- Test with known Engine assets (BasicShapes, materials)
- Verify successful responses and data formats

### Error Handling Tests
- Invalid asset paths and formats
- Non-existent assets and resources
- Permission and access issues
- Network connectivity problems

### Edge Cases
- Empty parameters and special characters
- Large asset lists and complex dependencies
- Concurrent operations
- Resource limits and timeouts

### Performance Tests
- Operation timing and response times
- Batch operation efficiency
- Memory usage during large operations
- Concurrent request handling

## Test Data

The tests use a combination of:

### Engine Assets (Always Available)
- `/Engine/BasicShapes/Cube` - Basic cube mesh
- `/Engine/BasicShapes/Sphere` - Basic sphere mesh
- `/Engine/BasicShapes/Cylinder` - Basic cylinder mesh
- `/Engine/BasicShapes/Plane` - Basic plane mesh
- `/Engine/EngineMaterials/DefaultMaterial` - Default material
- `/Engine/EngineMaterials/WorldGridMaterial` - Grid material

### Test Assets (Created/Cleaned Up)
- Temporary assets in `/Game/TestAssets/`
- Duplicated assets for manipulation testing
- Generated unique names to avoid conflicts

### Mock Data
- Predefined responses for offline testing
- Error conditions and edge cases
- Performance benchmarking data

## Asset Cleanup

The test framework includes comprehensive cleanup mechanisms:

### Automatic Cleanup
- Test assets are tracked during creation
- Cleanup occurs after test completion
- Error recovery attempts cleanup on failures

### Manual Cleanup
```python
from asset_test_utils import AssetTestUtils

with AssetTestUtils() as utils:
    # Test operations...
    pass  # Automatic cleanup on exit

# Or manual cleanup
utils = AssetTestUtils()
utils.cleanup_all()
```

## Validation and Verification

### Response Validation
- JSON structure and format validation
- Error message analysis and categorization
- Performance threshold checking
- Data consistency verification

### Asset State Validation
- Asset existence verification
- Metadata accuracy checking
- Dependency relationship validation
- Reference counting accuracy

## Test Results and Reporting

### Test Execution Results
- Individual test pass/fail status
- Error messages and diagnostics
- Performance metrics and timing
- Success rate and statistics

### Output Formats
- Console output with colored status indicators
- JSON results file with detailed information
- Performance analysis and slow test identification
- Error categorization and recovery suggestions

### Example Results Structure
```json
{
  "timestamp": 1755169662,
  "config": {
    "unreal_host": "127.0.0.1",
    "unreal_port": 55557,
    "use_mock_server": false
  },
  "summary": {
    "total_tests": 65,
    "passed_tests": 62,
    "failed_tests": 3,
    "success_rate": 95.4,
    "total_duration": 45.2
  },
  "results": [...]
}
```

## Dependencies

### Required Python Packages
- `asyncio` - Async test execution
- `json` - JSON data handling
- `pathlib` - Path manipulation
- `typing` - Type hints
- `pytest` (optional) - Test framework integration

### Unreal Engine Requirements
- Unreal Engine 5.6+ with UnrealMCP plugin
- TCP server running on configured port (default: 55557)
- Project with basic Engine assets available

## Best Practices

### Writing Asset Tests
1. **Use Engine Assets**: Prefer testing with Engine assets that are always available
2. **Clean Up Resources**: Always clean up test assets after operations
3. **Validate Responses**: Check both success and error conditions thoroughly
4. **Performance Awareness**: Monitor test execution times and resource usage
5. **Error Recovery**: Handle and test error conditions gracefully

### Test Organization
1. **Logical Grouping**: Group related tests by functionality
2. **Clear Naming**: Use descriptive test method names
3. **Documentation**: Document complex test scenarios
4. **Isolation**: Ensure tests don't depend on each other
5. **Repeatability**: Tests should be repeatable and deterministic

### Asset Management
1. **Unique Names**: Generate unique asset names to avoid conflicts
2. **Path Validation**: Validate asset paths before operations
3. **State Tracking**: Track created assets for cleanup
4. **Error Handling**: Handle asset operation failures gracefully
5. **Resource Limits**: Be aware of asset creation limits

## Troubleshooting

### Common Issues

#### Connection Failures
- Verify Unreal Engine is running with MCP plugin enabled
- Check host and port configuration
- Ensure firewall allows TCP connections
- Try mock server mode for development

#### Test Failures
- Check Unreal Engine logs for detailed error messages
- Verify Engine assets are available in the project
- Ensure adequate permissions for asset operations
- Review test data and expected results

#### Performance Issues
- Monitor system resources during test execution
- Consider reducing test parallelism
- Check network latency for remote connections
- Review asset complexity and operation scope

#### Asset Cleanup Issues
- Manually verify assets are cleaned up after tests
- Check for permission issues preventing deletion
- Review cleanup logs for specific failures
- Use asset browser to identify leftover test assets

### Debug Mode
Enable debug logging for detailed troubleshooting:

```bash
export UNREAL_MCP_LOG_STDERR=1
python run_asset_tests.py --verbose
```

## Contributing

When adding new asset tests:

1. **Follow Patterns**: Use existing test patterns and structure
2. **Add Cleanup**: Ensure new tests clean up created resources
3. **Document Tests**: Add clear docstrings and comments
4. **Test Coverage**: Include happy path, error, and edge cases
5. **Performance**: Consider performance impact of new tests

### Test Template
```python
def test_new_asset_operation(self):
    """Test description and expected behavior."""
    with self.framework.test_connection() as conn:
        assert conn.connect(), "Failed to connect to Unreal Engine"
        
        # Test setup
        test_asset = self.generate_unique_asset_path()
        
        # Execute operation
        response = conn.send_command("new_operation", {
            "asset_path": test_asset
        })
        
        # Validate results
        self._assert_valid_response(response, "new_operation")
        
        # Cleanup if needed
        if response.get("success"):
            self._add_cleanup_asset(test_asset)
        
        print(f"✓ New asset operation test completed")
```

## Version History

- **v1.0** - Initial comprehensive asset management test suite
  - Core asset operations testing
  - Content browser functionality testing
  - Asset registry operations testing
  - Test utilities and cleanup framework
  - Comprehensive test runner and reporting