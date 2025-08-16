#!/usr/bin/env python
"""
Test script for level and world management in Unreal Engine via MCP.

This script demonstrates the world/level management capabilities of the MCP system:
- Creating new levels
- Saving and loading levels
- Managing streaming levels
- Getting level information
- Basic landscape operations
- Error handling and validation
"""

import sys
import os
import time
import socket
import json
import logging
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import the server module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestLevelManagement")

def send_command(command: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Send a command to the Unreal MCP server and get the response.
    
    Args:
        command: The command type to send
        params: Dictionary of parameters for the command
        
    Returns:
        Optional[Dict[str, Any]]: The response from the server, or None if there was an error
    """
    try:
        # Create new socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 55557))
        
        # Prepare command
        command_data = {
            "command": command,
            "params": params
        }
        
        message = json.dumps(command_data) + "\n"
        sock.send(message.encode('utf-8'))
        
        # Receive response
        response_data = sock.recv(4096).decode('utf-8')
        sock.close()
        
        if response_data:
            return json.loads(response_data)
        
    except Exception as e:
        logger.error(f"Error sending command {command}: {e}")
    
    return None

def test_level_info():
    """Test getting current level information."""
    logger.info("Testing get_current_level_info...")
    
    response = send_command("get_current_level_info", {})
    if response:
        if response.get("success"):
            result = response.get("result", {})
            logger.info(f"Current world name: {result.get('world_name', 'Unknown')}")
            logger.info(f"World type: {result.get('world_type', 'Unknown')}")
            logger.info(f"Number of levels: {result.get('num_levels', 0)}")
            
            if "persistent_level" in result:
                persistent_level = result["persistent_level"]
                logger.info(f"Persistent level: {persistent_level.get('name', 'Unknown')}")
                logger.info(f"Number of actors: {persistent_level.get('num_actors', 0)}")
            
            streaming_levels = result.get("streaming_levels", [])
            logger.info(f"Number of streaming levels: {len(streaming_levels)}")
            for i, level in enumerate(streaming_levels):
                logger.info(f"  Streaming level {i+1}: {level.get('package_name', 'Unknown')} "
                          f"(loaded: {level.get('is_loaded', False)}, visible: {level.get('is_visible', False)})")
        else:
            logger.error(f"Failed to get level info: {response.get('error', 'Unknown error')}")
    else:
        logger.error("No response received")

def test_save_level():
    """Test saving the current level."""
    logger.info("Testing save_level...")
    
    response = send_command("save_level", {})
    if response:
        if response.get("success"):
            logger.info(f"Level saved: {response.get('result', 'Success')}")
        else:
            logger.error(f"Failed to save level: {response.get('error', 'Unknown error')}")
    else:
        logger.error("No response received")

def test_create_level():
    """Test creating a new level."""
    logger.info("Testing create_level...")
    
    test_level_name = f"TestLevel_{int(time.time())}"
    response = send_command("create_level", {"level_name": test_level_name})
    
    if response:
        if response.get("success"):
            result = response.get("result", {})
            logger.info(f"Created level: {test_level_name}")
            logger.info(f"Level info: {result}")
        else:
            logger.error(f"Failed to create level: {response.get('error', 'Unknown error')}")
    else:
        logger.error("No response received")
    
    return test_level_name

def test_level_visibility():
    """Test setting level visibility."""
    logger.info("Testing set_level_visibility...")
    
    # Try to set visibility for the persistent level (this might not work as expected)
    response = send_command("set_level_visibility", {
        "level_name": "Persistent Level",
        "visible": False
    })
    
    if response:
        if response.get("success"):
            logger.info(f"Set level visibility: {response.get('result', 'Success')}")
        else:
            logger.warning(f"Failed to set level visibility (expected for persistent level): {response.get('error', 'Unknown error')}")
    else:
        logger.error("No response received")

def test_streaming_level():
    """Test streaming level operations."""
    logger.info("Testing streaming level operations...")
    
    # Test creating a streaming level
    test_stream_level = "/Game/TestStreamingLevel"
    response = send_command("create_streaming_level", {"level_path": test_stream_level})
    
    if response:
        if response.get("success"):
            logger.info(f"Created streaming level: {response.get('result', 'Success')}")
            
            # Test loading the streaming level
            time.sleep(1)  # Give it a moment
            response = send_command("load_streaming_level", {"level_name": "TestStreamingLevel"})
            
            if response and response.get("success"):
                logger.info(f"Loaded streaming level: {response.get('result', 'Success')}")
                
                # Test unloading the streaming level
                time.sleep(1)
                response = send_command("unload_streaming_level", {"level_name": "TestStreamingLevel"})
                
                if response and response.get("success"):
                    logger.info(f"Unloaded streaming level: {response.get('result', 'Success')}")
                else:
                    logger.warning(f"Failed to unload streaming level: {response.get('error', 'Unknown error') if response else 'No response'}")
            else:
                logger.warning(f"Failed to load streaming level: {response.get('error', 'Unknown error') if response else 'No response'}")
        else:
            logger.warning(f"Failed to create streaming level: {response.get('error', 'Unknown error')}")
    else:
        logger.error("No response received")

def test_landscape_operations():
    """Test landscape creation and information retrieval."""
    logger.info("Testing landscape operations...")
    
    # Test getting landscape info
    response = send_command("get_landscape_info", {})
    if response:
        if response.get("success"):
            result = response.get("result", {})
            landscapes = result.get("landscapes", [])
            logger.info(f"Found {len(landscapes)} landscapes in the level")
            
            for i, landscape in enumerate(landscapes):
                logger.info(f"  Landscape {i+1}: {landscape.get('name', 'Unknown')}")
                location = landscape.get("location", {})
                logger.info(f"    Location: ({location.get('x', 0)}, {location.get('y', 0)}, {location.get('z', 0)})")
                size_x = landscape.get("size_x", "Unknown")
                size_y = landscape.get("size_y", "Unknown")
                logger.info(f"    Size: {size_x} x {size_y}")
        else:
            logger.warning(f"Failed to get landscape info: {response.get('error', 'Unknown error')}")
    else:
        logger.error("No response received")
    
    # Test creating a landscape
    logger.info("Testing create_landscape...")
    response = send_command("create_landscape", {
        "size_x": 127,
        "size_y": 127,
        "location": {"x": 0, "y": 0, "z": 100}
    })
    
    if response:
        if response.get("success"):
            result = response.get("result", {})
            logger.info(f"Landscape creation initiated: {result}")
        else:
            logger.warning(f"Failed to create landscape: {response.get('error', 'Unknown error')}")
    else:
        logger.error("No response received")

def main():
    """Run all tests."""
    logger.info("Starting Level Management Tests")
    logger.info("=" * 50)
    
    try:
        # Test connection first
        logger.info("Testing connection to Unreal Engine...")
        test_response = send_command("get_current_level_info", {})
        if not test_response:
            logger.error("Cannot connect to Unreal Engine. Make sure:")
            logger.error("1. Unreal Engine is running")
            logger.error("2. The UnrealMCP plugin is loaded")
            logger.error("3. The MCP server is listening on port 55557")
            return
        
        logger.info("Connection successful!")
        
        # Run tests
        test_level_info()
        logger.info("-" * 30)
        
        test_save_level()
        logger.info("-" * 30)
        
        test_level_name = test_create_level()
        logger.info("-" * 30)
        
        test_level_visibility()
        logger.info("-" * 30)
        
        test_streaming_level()
        logger.info("-" * 30)
        
        test_landscape_operations()
        
        logger.info("=" * 50)
        logger.info("Level Management Tests Completed!")
        
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()