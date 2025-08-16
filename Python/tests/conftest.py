"""
Pytest configuration and fixtures for Unreal MCP testing.

Provides shared fixtures, test configuration, and pytest integration
for the Unreal MCP test suite.
"""

import os
import sys
import pytest
import logging
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_framework import TestFramework, TestConfig, create_test_config, MockUnrealServer
from test_results import TestResultCollector, TestRunResults
from unreal_mcp_server import UnrealConnection

# Configure pytest logging
def pytest_configure(config):
    """Configure pytest with custom settings."""
    logging.basicConfig(
        level=logging.DEBUG if config.getoption("--verbose") else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pytest_execution.log')
        ]
    )

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--unreal-host",
        action="store",
        default="127.0.0.1",
        help="Unreal Engine host address"
    )
    parser.addoption(
        "--unreal-port", 
        action="store",
        type=int,
        default=55557,
        help="Unreal Engine port number"
    )
    parser.addoption(
        "--use-mock",
        action="store_true",
        default=False,
        help="Use mock Unreal server for testing"
    )
    parser.addoption(
        "--integration-only",
        action="store_true",
        default=False,
        help="Run only integration tests"
    )
    parser.addoption(
        "--unit-only",
        action="store_true", 
        default=False,
        help="Run only unit tests"
    )
    parser.addoption(
        "--validation-only",
        action="store_true",
        default=False,
        help="Run only validation tests"
    )
    parser.addoption(
        "--skip-connection-test",
        action="store_true",
        default=False,
        help="Skip initial Unreal connection test"
    )
    parser.addoption(
        "--test-timeout",
        action="store",
        type=float,
        default=30.0,
        help="Individual test timeout in seconds"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    integration_only = config.getoption("--integration-only")
    unit_only = config.getoption("--unit-only") 
    validation_only = config.getoption("--validation-only")
    
    if integration_only:
        # Skip non-integration tests
        skip_marker = pytest.mark.skip(reason="--integration-only specified")
        for item in items:
            if "integration" not in str(item.fspath):
                item.add_marker(skip_marker)
                
    elif unit_only:
        # Skip non-unit tests
        skip_marker = pytest.mark.skip(reason="--unit-only specified")
        for item in items:
            if "unit" not in str(item.fspath):
                item.add_marker(skip_marker)
                
    elif validation_only:
        # Skip non-validation tests
        skip_marker = pytest.mark.skip(reason="--validation-only specified")
        for item in items:
            if "validation" not in str(item.fspath):
                item.add_marker(skip_marker)

def pytest_runtest_setup(item):
    """Setup for individual tests."""
    # Check if Unreal connection is required and working
    if hasattr(item, 'pytestmark'):
        for mark in item.pytestmark:
            if mark.name == 'requires_unreal':
                if item.config.getoption("--use-mock"):
                    # Skip connection check when using mock
                    continue
                    
                if not item.config.getoption("--skip-connection-test"):
                    # Test Unreal connection
                    config = create_test_config(
                        unreal_host=item.config.getoption("--unreal-host"),
                        unreal_port=item.config.getoption("--unreal-port")
                    )
                    framework = TestFramework(config)
                    if not framework.test_unreal_connection():
                        pytest.skip("Unreal Engine connection not available")

@pytest.fixture(scope="session")
def test_config(request) -> TestConfig:
    """Create test configuration from command line options."""
    return create_test_config(
        use_mock=request.config.getoption("--use-mock"),
        unreal_host=request.config.getoption("--unreal-host"),
        unreal_port=request.config.getoption("--unreal-port"),
        command_timeout=request.config.getoption("--test-timeout")
    )

@pytest.fixture(scope="session")
def mock_server(test_config) -> Generator[MockUnrealServer, None, None]:
    """Provide a mock Unreal server for testing."""
    if test_config.use_mock_server:
        server = MockUnrealServer(test_config.unreal_host, test_config.unreal_port)
        server.start()
        yield server
        server.stop()
    else:
        yield None

@pytest.fixture
def test_framework(test_config, mock_server) -> TestFramework:
    """Create a test framework instance."""
    framework = TestFramework(test_config)
    if mock_server:
        # Set up default mock responses
        mock_server.set_mock_response("get_actors_in_level", {
            "success": True,
            "result": []
        })
        mock_server.set_mock_response("spawn_actor", {
            "success": True,
            "result": "Test actor spawned"
        })
        mock_server.set_mock_response("delete_actor", {
            "success": True,
            "result": "Test actor deleted"
        })
    return framework

@pytest.fixture
def unreal_connection(test_config, mock_server) -> Generator[UnrealConnection, None, None]:
    """Provide an Unreal connection for testing."""
    if test_config.use_mock_server and mock_server:
        # Use test connection that points to mock server
        from test_framework import TestUnrealConnection
        connection = TestUnrealConnection(test_config)
    else:
        connection = UnrealConnection()
    
    yield connection
    
    # Cleanup
    if connection.connected:
        connection.disconnect()

@pytest.fixture
def result_collector() -> TestResultCollector:
    """Provide a test result collector."""
    collector = TestResultCollector()
    collector.start_test_run()
    return collector

@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def sample_test_data() -> Dict[str, Any]:
    """Provide sample test data for various test scenarios."""
    return {
        "actors": [
            {
                "name": "TestCube",
                "type": "StaticMeshActor",
                "location": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1]
            },
            {
                "name": "TestSphere", 
                "type": "StaticMeshActor",
                "location": [100, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1]
            }
        ],
        "blueprints": [
            {
                "name": "TestBlueprint",
                "parent_class": "Actor",
                "components": [
                    {
                        "type": "StaticMeshComponent",
                        "name": "StaticMesh"
                    },
                    {
                        "type": "BoxCollisionComponent", 
                        "name": "CollisionBox"
                    }
                ]
            }
        ],
        "commands": {
            "get_actors_in_level": {},
            "spawn_actor": {
                "name": "TestActor",
                "type": "StaticMeshActor",
                "location": [0, 0, 0]
            },
            "delete_actor": {
                "name": "TestActor"
            }
        },
        "expected_responses": {
            "get_actors_in_level": {
                "success": True,
                "result": []
            },
            "spawn_actor": {
                "success": True, 
                "result": "Actor spawned successfully"
            },
            "delete_actor": {
                "success": True,
                "result": "Actor deleted successfully"
            }
        },
        "error_cases": {
            "invalid_command": {
                "command": "nonexistent_command",
                "expected_error": "Unknown command"
            },
            "missing_params": {
                "command": "spawn_actor",
                "params": {},  # Missing required params
                "expected_error": "Missing required parameter"
            }
        }
    }

@pytest.fixture
def async_test_runner():
    """Provide async test runner utilities."""
    class AsyncTestRunner:
        @staticmethod
        async def run_async_test(async_func, *args, **kwargs):
            """Run an async test function."""
            return await async_func(*args, **kwargs)
            
        @staticmethod
        def run_in_event_loop(async_func, *args, **kwargs):
            """Run async function in event loop."""
            return asyncio.run(async_func(*args, **kwargs))
    
    return AsyncTestRunner()

# Test markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "requires_unreal: mark test as requiring Unreal Engine connection"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "validation: mark test as validation test"
    )
    config.addinivalue_line(
        "markers", "actors: mark test as testing actor functionality"
    )
    config.addinivalue_line(
        "markers", "blueprints: mark test as testing blueprint functionality"
    )
    config.addinivalue_line(
        "markers", "assets: mark test as testing asset functionality"
    )
    config.addinivalue_line(
        "markers", "umg: mark test as testing UMG functionality"
    )
    config.addinivalue_line(
        "markers", "world: mark test as testing world functionality"
    )

# Pytest plugins for better reporting
pytest_plugins = [
    "pytest_html",  # HTML reports
    "pytest_json_report",  # JSON reports
    "pytest_xdist",  # Parallel execution
]

# Custom pytest hooks for result collection
def pytest_runtest_makereport(item, call):
    """Custom test result reporting."""
    if call.when == "call":
        # Extract test information
        test_name = item.nodeid
        duration = call.duration
        
        # Check if we have a result collector
        if hasattr(item.session, 'test_result_collector'):
            collector = item.session.test_result_collector
            
            if call.excinfo is None:
                # Test passed
                collector.add_test_result(test_name, True, duration)
            else:
                # Test failed or error
                error_msg = str(call.excinfo.value) if call.excinfo.value else "Unknown error"
                collector.add_test_result(test_name, False, duration, error=error_msg)

def pytest_sessionstart(session):
    """Initialize session-wide test result collection."""
    session.test_result_collector = TestResultCollector()
    session.test_result_collector.start_test_run()

def pytest_sessionfinish(session):
    """Finalize session-wide test result collection."""
    if hasattr(session, 'test_result_collector'):
        results = session.test_result_collector.complete_test_run()
        
        # Save results to file
        from test_results import TestResultReporter
        reporter = TestResultReporter(results)
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Save reports
        reporter.save_reports(str(output_dir))
        
        print(f"\nTest results saved to {output_dir}/")
        print(f"View HTML report: {output_dir}/test_report.html")

# Helper functions for tests
def assert_unreal_response_success(response: Dict[str, Any], message: str = ""):
    """Assert that an Unreal response indicates success."""
    assert response is not None, f"No response received. {message}"
    assert response.get("status") != "error", f"Command failed: {response.get('error', 'Unknown error')}. {message}"
    assert response.get("success") is not False, f"Command failed: {response.get('error', response.get('message', 'Unknown error'))}. {message}"

def assert_unreal_response_error(response: Dict[str, Any], expected_error: str = None):
    """Assert that an Unreal response indicates an error."""
    assert response is not None, "Expected error response but got no response"
    assert response.get("status") == "error" or response.get("success") is False, f"Expected error but got success response: {response}"
    if expected_error:
        error_msg = response.get("error", response.get("message", ""))
        assert expected_error in str(error_msg), f"Expected error '{expected_error}' but got '{error_msg}'"