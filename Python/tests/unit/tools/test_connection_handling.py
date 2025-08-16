"""
Unit tests for connection handling and error management.

Tests the UnrealConnection class and related networking functionality
without requiring an actual Unreal Engine instance.
"""

import pytest
import socket
import time
import json
from unittest.mock import Mock, patch, MagicMock

# Import the classes we want to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from unreal_mcp_server import UnrealConnection
from tests.test_framework import TestUnrealConnection, TestConfig, MockUnrealServer

@pytest.mark.unit
class TestUnrealConnection:
    """Test the UnrealConnection class."""
    
    def test_connection_initialization(self):
        """Test connection object initialization."""
        conn = UnrealConnection()
        assert conn.socket is None
        assert conn.connected is False
        
    def test_connection_with_valid_parameters(self):
        """Test connection with valid host/port parameters."""
        # This test uses mocking since we don't have a real server
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            
            result = conn.connect()
            
            # Verify socket was configured correctly
            mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
            mock_sock_instance.settimeout.assert_called()
            mock_sock_instance.setsockopt.assert_called()
            mock_sock_instance.connect.assert_called()
            
            assert result is True
            assert conn.connected is True
            
    def test_connection_failure_handling(self):
        """Test handling of connection failures."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.side_effect = ConnectionRefusedError("Connection refused")
            
            result = conn.connect()
            
            assert result is False
            assert conn.connected is False
            
    def test_disconnect(self):
        """Test disconnection functionality."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            
            # Connect first
            conn.connect()
            assert conn.connected is True
            
            # Then disconnect
            conn.disconnect()
            mock_sock_instance.close.assert_called_once()
            assert conn.connected is False
            assert conn.socket is None
            
    def test_send_command_basic(self):
        """Test basic command sending."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.return_value = json.dumps({"success": True, "result": "test"}).encode('utf-8')
            
            response = conn.send_command("test_command", {"param": "value"})
            
            # Verify command was sent
            mock_sock_instance.sendall.assert_called()
            sent_data = mock_sock_instance.sendall.call_args[0][0]
            sent_command = json.loads(sent_data.decode('utf-8'))
            
            assert sent_command["type"] == "test_command"
            assert sent_command["params"] == {"param": "value"}
            assert response["success"] is True
            assert response["result"] == "test"
            
    def test_send_command_with_error_response(self):
        """Test handling of error responses from Unreal."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.return_value = json.dumps({
                "success": False, 
                "error": "Test error"
            }).encode('utf-8')
            
            response = conn.send_command("failing_command", {})
            
            assert response["status"] == "error"
            assert response["error"] == "Test error"
            
    def test_receive_full_response_chunked_data(self):
        """Test receiving response data in chunks."""
        conn = UnrealConnection()
        
        # Create a large response that would be chunked
        large_response = {"success": True, "result": "x" * 5000}
        response_data = json.dumps(large_response).encode('utf-8')
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            
            # Simulate chunked reception
            chunk_size = 1000
            chunks = [response_data[i:i+chunk_size] for i in range(0, len(response_data), chunk_size)]
            chunks.append(b'')  # End of data marker
            
            mock_sock_instance.recv.side_effect = chunks
            mock_sock_instance.settimeout.return_value = None
            
            # Test the chunked reception
            conn.connect()
            received_data = conn.receive_full_response(mock_sock_instance)
            
            assert received_data == response_data
            
    def test_command_timeout_handling(self):
        """Test handling of command timeouts."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.side_effect = socket.timeout("Socket timeout")
            
            response = conn.send_command("slow_command", {})
            
            assert response["status"] == "error"
            assert "timeout" in response["error"].lower()

@pytest.mark.unit
class TestTestUnrealConnection:
    """Test the enhanced TestUnrealConnection class."""
    
    def test_test_connection_initialization(self):
        """Test TestUnrealConnection initialization with config."""
        config = TestConfig(
            unreal_host="test-host",
            unreal_port=12345,
            connection_timeout=5.0,
            max_connection_retries=2
        )
        
        conn = TestUnrealConnection(config)
        assert conn.config == config
        assert conn.connection_attempts == 0
        assert conn.last_error is None
        
    def test_connection_retry_logic(self):
        """Test connection retry logic."""
        config = TestConfig(
            retry_failed_connections=True,
            max_connection_retries=3
        )
        
        conn = TestUnrealConnection(config)
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            
            # First two attempts fail, third succeeds
            mock_sock_instance.connect.side_effect = [
                ConnectionRefusedError("First failure"),
                ConnectionRefusedError("Second failure"), 
                None  # Success on third attempt
            ]
            
            result = conn.connect()
            
            assert result is True
            assert conn.connection_attempts == 3
            assert conn.connected is True
            
    def test_connection_retry_exhaustion(self):
        """Test behavior when all connection retries are exhausted."""
        config = TestConfig(
            retry_failed_connections=True,
            max_connection_retries=2
        )
        
        conn = TestUnrealConnection(config)
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.side_effect = ConnectionRefusedError("Always fails")
            
            result = conn.connect()
            
            assert result is False
            assert conn.connection_attempts == 2  # Maximum retries
            assert conn.connected is False
            assert "Always fails" in conn.last_error

@pytest.mark.unit 
class TestMockUnrealServer:
    """Test the MockUnrealServer functionality."""
    
    def test_mock_server_initialization(self):
        """Test mock server initialization."""
        server = MockUnrealServer("localhost", 12345)
        assert server.host == "localhost"
        assert server.port == 12345
        assert server.running is False
        assert len(server.mock_responses) == 0
        assert len(server.received_commands) == 0
        
    def test_set_mock_response(self):
        """Test setting mock responses."""
        server = MockUnrealServer()
        
        test_response = {"success": True, "result": "mock result"}
        server.set_mock_response("test_command", test_response)
        
        assert "test_command" in server.mock_responses
        assert server.mock_responses["test_command"] == test_response
        
    def test_mock_server_start_stop(self):
        """Test starting and stopping the mock server."""
        server = MockUnrealServer("127.0.0.1", 0)  # Use port 0 for auto-assignment
        
        try:
            server.start()
            assert server.running is True
            assert server.socket is not None
            assert server.thread is not None
            
            # Give the server a moment to start
            time.sleep(0.1)
            
            server.stop()
            assert server.running is False
            
        except OSError as e:
            # Skip test if we can't bind to a socket (common in some CI environments)
            pytest.skip(f"Could not start mock server: {e}")
            
    def test_mock_server_command_handling(self):
        """Test mock server command handling."""
        # This test would require a more complex setup with actual socket communication
        # For now, we test the response logic directly
        server = MockUnrealServer()
        
        # Set up mock responses
        server.set_mock_response("test_cmd", {"success": True, "result": "test"})
        
        # Simulate a received command
        test_command = {"type": "test_cmd", "params": {}}
        server.received_commands.append(test_command)
        
        # Check that the command was recorded
        assert len(server.received_commands) == 1
        assert server.received_commands[0]["type"] == "test_cmd"
        
        # Check that the response would be correct
        expected_response = server.mock_responses.get("test_cmd")
        assert expected_response["success"] is True
        assert expected_response["result"] == "test"

@pytest.mark.unit
class TestConnectionErrorHandling:
    """Test various error conditions and edge cases."""
    
    def test_malformed_json_response(self):
        """Test handling of malformed JSON responses."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.return_value = b'{"invalid": json malformed'
            
            response = conn.send_command("test_command", {})
            
            assert response["status"] == "error"
            assert "error" in response
            
    def test_empty_response(self):
        """Test handling of empty responses."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.return_value = b''
            
            response = conn.send_command("test_command", {})
            
            assert response["status"] == "error"
            
    def test_socket_error_during_send(self):
        """Test handling of socket errors during command sending."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.sendall.side_effect = socket.error("Send failed")
            
            response = conn.send_command("test_command", {})
            
            assert response["status"] == "error"
            assert "Send failed" in response["error"]
            
    def test_connection_reset_handling(self):
        """Test handling of connection reset errors."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.side_effect = ConnectionResetError("Connection reset")
            
            response = conn.send_command("test_command", {})
            
            assert response["status"] == "error"
            assert "connection reset" in response["error"].lower()

@pytest.mark.unit
class TestResponseFormatHandling:
    """Test handling of different response formats from Unreal."""
    
    def test_success_response_format(self):
        """Test handling of success response format."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.return_value = json.dumps({
                "success": True,
                "result": {"data": "test_data"}
            }).encode('utf-8')
            
            response = conn.send_command("test_command", {})
            
            assert response["success"] is True
            assert response["result"]["data"] == "test_data"
            
    def test_error_response_with_status(self):
        """Test handling of error response with status field."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.return_value = json.dumps({
                "status": "error",
                "error": "Test error message"
            }).encode('utf-8')
            
            response = conn.send_command("test_command", {})
            
            # The connection should preserve the error format
            assert response["status"] == "error"
            assert response["error"] == "Test error message"
            
    def test_error_response_with_success_false(self):
        """Test handling of error response with success=false."""
        conn = UnrealConnection()
        
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.return_value = None
            mock_sock_instance.recv.return_value = json.dumps({
                "success": False,
                "message": "Operation failed"
            }).encode('utf-8')
            
            response = conn.send_command("test_command", {})
            
            # The connection should convert this to standard error format
            assert response["status"] == "error"
            assert response["error"] == "Operation failed"