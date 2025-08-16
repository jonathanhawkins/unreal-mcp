"""
Core testing framework for Unreal MCP tools.

Provides infrastructure for testing MCP tools including:
- TCP connection management and mocking
- Test setup/teardown with proper cleanup
- Unreal Engine connection testing
- Mock server capability for offline testing
- Error handling and timeout management
"""

import asyncio
import json
import logging
import os
import socket
import time
import threading
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, AsyncIterator
from unittest.mock import Mock, MagicMock
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unreal_mcp_server import UnrealConnection, get_unreal_connection

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Result of a single test execution."""
    name: str
    success: bool
    error: Optional[str] = None
    duration: float = 0.0
    output: List[str] = field(default_factory=list)
    skipped: bool = False
    skip_reason: Optional[str] = None

@dataclass 
class TestConfig:
    """Configuration for test execution."""
    unreal_host: str = "127.0.0.1"
    unreal_port: int = 55557
    connection_timeout: float = 10.0
    command_timeout: float = 30.0
    use_mock_server: bool = False
    mock_responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    cleanup_on_failure: bool = True
    retry_failed_connections: bool = True
    max_connection_retries: int = 3
    parallel_execution: bool = False
    max_workers: int = 4

class MockUnrealServer:
    """Mock Unreal Engine server for offline testing."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 55558):
        self.host = host
        self.port = port
        self.socket = None
        self.thread = None
        self.running = False
        self.mock_responses = {}
        self.received_commands = []
        
    def set_mock_response(self, command: str, response: Dict[str, Any]):
        """Set a mock response for a specific command."""
        self.mock_responses[command] = response
        
    def start(self):
        """Start the mock server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        
        self.thread = threading.Thread(target=self._server_loop, daemon=True)
        self.thread.start()
        
        # Wait for server to be ready
        time.sleep(0.1)
        logger.info(f"Mock Unreal server started on {self.host}:{self.port}")
        
    def stop(self):
        """Stop the mock server."""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join(timeout=1)
        logger.info("Mock Unreal server stopped")
        
    def _server_loop(self):
        """Main server loop."""
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                ).start()
            except OSError:
                # Socket was closed
                break
            except Exception as e:
                if self.running:
                    logger.error(f"Mock server error: {e}")
                    
    def _handle_client(self, client_socket):
        """Handle a client connection."""
        try:
            # Receive command
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                return
                
            command_obj = json.loads(data)
            command_type = command_obj.get('type', '')
            self.received_commands.append(command_obj)
            
            # Get mock response
            response = self.mock_responses.get(
                command_type,
                {"success": True, "result": f"Mock response for {command_type}"}
            )
            
            # Send response
            response_json = json.dumps(response)
            client_socket.sendall(response_json.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Mock server client handler error: {e}")
        finally:
            client_socket.close()

class TestUnrealConnection(UnrealConnection):
    """Extended UnrealConnection for testing with additional features."""
    
    def __init__(self, config: TestConfig):
        super().__init__()
        self.config = config
        self.connection_attempts = 0
        self.last_error = None
        
    def connect(self) -> bool:
        """Connect with retry logic and timeout configuration."""
        self.connection_attempts += 1
        
        try:
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            
            logger.debug(f"Connecting to Unreal at {self.config.unreal_host}:{self.config.unreal_port} (attempt {self.connection_attempts})")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config.connection_timeout)
            
            # Set socket options for testing
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            
            self.socket.connect((self.config.unreal_host, self.config.unreal_port))
            self.connected = True
            logger.debug(f"Connected to Unreal Engine successfully")
            return True
            
        except Exception as e:
            self.last_error = str(e)
            logger.warning(f"Connection attempt {self.connection_attempts} failed: {e}")
            self.connected = False
            
            if self.config.retry_failed_connections and self.connection_attempts < self.config.max_connection_retries:
                time.sleep(0.5)  # Brief delay before retry
                return self.connect()
                
            return False

class TestFramework:
    """Main testing framework for Unreal MCP tools."""
    
    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.mock_server = None
        self.connection = None
        self.setup_functions = []
        self.teardown_functions = []
        self.test_results = []
        self.cleanup_functions = []
        
    def setup_logging(self, level: int = logging.INFO):
        """Configure logging for tests."""
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('test_execution.log')
            ]
        )
        
    def add_setup(self, func: Callable):
        """Add a setup function to run before tests."""
        self.setup_functions.append(func)
        
    def add_teardown(self, func: Callable):
        """Add a teardown function to run after tests."""
        self.teardown_functions.append(func)
        
    def add_cleanup(self, func: Callable):
        """Add a cleanup function to run on test failure."""
        self.cleanup_functions.append(func)
        
    @contextmanager
    def test_connection(self):
        """Context manager for test connection with automatic cleanup."""
        if self.config.use_mock_server:
            # Use mock server
            self.mock_server = MockUnrealServer(
                self.config.unreal_host, 
                self.config.unreal_port
            )
            for command, response in self.config.mock_responses.items():
                self.mock_server.set_mock_response(command, response)
            self.mock_server.start()
            
        try:
            self.connection = TestUnrealConnection(self.config)
            yield self.connection
        finally:
            if self.connection:
                self.connection.disconnect()
            if self.mock_server:
                self.mock_server.stop()
                
    def run_setup(self):
        """Run all setup functions."""
        for setup_func in self.setup_functions:
            try:
                setup_func()
            except Exception as e:
                logger.error(f"Setup function failed: {e}")
                raise
                
    def run_teardown(self):
        """Run all teardown functions."""
        for teardown_func in self.teardown_functions:
            try:
                teardown_func()
            except Exception as e:
                logger.error(f"Teardown function failed: {e}")
                
    def run_cleanup(self):
        """Run all cleanup functions."""
        for cleanup_func in self.cleanup_functions:
            try:
                cleanup_func()
            except Exception as e:
                logger.error(f"Cleanup function failed: {e}")
                
    def test_unreal_connection(self) -> bool:
        """Test if connection to Unreal Engine is working."""
        try:
            with self.test_connection() as conn:
                if not conn.connect():
                    logger.error("Failed to connect to Unreal Engine")
                    return False
                    
                # Test a simple command
                response = conn.send_command("get_actors_in_level", {})
                if response and response.get("status") != "error":
                    logger.info("Unreal Engine connection test successful")
                    return True
                else:
                    logger.error(f"Unreal Engine command test failed: {response}")
                    return False
                    
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
            
    async def run_test(self, test_func: Callable, test_name: str) -> TestResult:
        """Run a single test function."""
        start_time = time.time()
        result = TestResult(name=test_name, success=False)
        
        try:
            logger.info(f"Running test: {test_name}")
            
            # Run the test function
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
                
            result.success = True
            logger.info(f"Test {test_name} passed")
            
        except AssertionError as e:
            result.error = f"Assertion failed: {str(e)}"
            logger.error(f"Test {test_name} failed: {result.error}")
            if self.config.cleanup_on_failure:
                self.run_cleanup()
                
        except Exception as e:
            result.error = f"Test error: {str(e)}"
            logger.error(f"Test {test_name} error: {result.error}")
            if self.config.cleanup_on_failure:
                self.run_cleanup()
                
        finally:
            result.duration = time.time() - start_time
            
        return result
        
    def skip_test(self, test_name: str, reason: str) -> TestResult:
        """Mark a test as skipped."""
        return TestResult(
            name=test_name,
            success=False,
            skipped=True,
            skip_reason=reason
        )
        
    def assert_response_success(self, response: Dict[str, Any], message: str = ""):
        """Assert that a response indicates success."""
        if not response:
            raise AssertionError(f"No response received. {message}")
        if response.get("status") == "error":
            error_msg = response.get("error", "Unknown error")
            raise AssertionError(f"Command failed: {error_msg}. {message}")
        if response.get("success") is False:
            error_msg = response.get("error", response.get("message", "Unknown error"))
            raise AssertionError(f"Command failed: {error_msg}. {message}")
            
    def assert_response_error(self, response: Dict[str, Any], expected_error: str = None):
        """Assert that a response indicates an error."""
        if not response:
            raise AssertionError("Expected error response but got no response")
        if response.get("status") != "error" and response.get("success") is not False:
            raise AssertionError(f"Expected error but got success response: {response}")
        if expected_error and expected_error not in str(response.get("error", "")):
            raise AssertionError(f"Expected error '{expected_error}' but got '{response.get('error')}'")
            
    def assert_actors_exist(self, actor_names: List[str]):
        """Assert that specific actors exist in the level."""
        with self.test_connection() as conn:
            response = conn.send_command("get_actors_in_level", {})
            self.assert_response_success(response, "Failed to get actors in level")
            
            existing_actors = response.get("result", [])
            for actor_name in actor_names:
                if not any(actor.get("name") == actor_name for actor in existing_actors):
                    raise AssertionError(f"Actor '{actor_name}' not found in level")
                    
    def assert_actors_not_exist(self, actor_names: List[str]):
        """Assert that specific actors do not exist in the level."""
        with self.test_connection() as conn:
            response = conn.send_command("get_actors_in_level", {})
            self.assert_response_success(response, "Failed to get actors in level")
            
            existing_actors = response.get("result", [])
            for actor_name in actor_names:
                if any(actor.get("name") == actor_name for actor in existing_actors):
                    raise AssertionError(f"Actor '{actor_name}' should not exist in level")

def create_test_config(
    use_mock: bool = False,
    unreal_host: str = "127.0.0.1",
    unreal_port: int = 55557,
    **kwargs
) -> TestConfig:
    """Create a test configuration with common defaults."""
    config = TestConfig(
        unreal_host=unreal_host,
        unreal_port=unreal_port,
        use_mock_server=use_mock,
        **kwargs
    )
    
    # Override with environment variables if present
    config.unreal_host = os.environ.get("TEST_UNREAL_HOST", config.unreal_host)
    config.unreal_port = int(os.environ.get("TEST_UNREAL_PORT", str(config.unreal_port)))
    config.connection_timeout = float(os.environ.get("TEST_CONNECTION_TIMEOUT", str(config.connection_timeout)))
    config.command_timeout = float(os.environ.get("TEST_COMMAND_TIMEOUT", str(config.command_timeout)))
    config.use_mock_server = os.environ.get("TEST_USE_MOCK", "false").lower() == "true"
    
    return config

# Global test framework instance
_test_framework = None

def get_test_framework(config: TestConfig = None) -> TestFramework:
    """Get or create the global test framework instance."""
    global _test_framework
    if _test_framework is None:
        _test_framework = TestFramework(config)
    return _test_framework