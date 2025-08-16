"""
Integration tests for project-level MCP commands.

Tests project configuration and settings commands.
"""

import pytest
import asyncio
from typing import Dict, Any
from Python.unreal_mcp_client import UnrealMCPClient


class TestProjectCommands:
    """Test suite for project-level commands."""
    
    @pytest.fixture
    async def mcp_client(self):
        """Create an MCP client for testing."""
        client = UnrealMCPClient()
        await client.connect()
        yield client
        await client.disconnect()
    
    async def test_create_input_mapping_action(self, mcp_client: UnrealMCPClient):
        """Test creating an action input mapping."""
        response = await mcp_client.send_command("create_input_mapping", {
            "action_name": "TestJump",
            "key": "Space"
        })
        
        assert response["success"] is True
        assert response.get("action_name") == "TestJump"
        assert response.get("key") == "Space"
    
    async def test_create_input_mapping_with_modifiers(self, mcp_client: UnrealMCPClient):
        """Test creating input mapping with modifiers."""
        response = await mcp_client.send_command("create_input_mapping", {
            "action_name": "TestSave",
            "key": "S",
            "shift": False,
            "ctrl": True,
            "alt": False,
            "cmd": False
        })
        
        assert response["success"] is True
        assert response.get("action_name") == "TestSave"
        assert response.get("key") == "S"
    
    async def test_create_input_mapping_axis(self, mcp_client: UnrealMCPClient):
        """Test creating an axis input mapping."""
        response = await mcp_client.send_command("create_input_mapping", {
            "axis_name": "TestMoveForward",
            "key": "W",
            "scale": 1.0
        })
        
        # Check if axis mappings are supported
        if response["success"]:
            assert "axis_name" in response or "action_name" in response
        else:
            # Axis might not be supported, try as action
            response = await mcp_client.send_command("create_input_mapping", {
                "action_name": "TestMoveForward",
                "key": "W"
            })
            assert response["success"] is True
    
    async def test_create_multiple_input_mappings(self, mcp_client: UnrealMCPClient):
        """Test creating multiple input mappings."""
        mappings = [
            {"action_name": "TestFire", "key": "LeftMouseButton"},
            {"action_name": "TestReload", "key": "R"},
            {"action_name": "TestCrouch", "key": "C"},
            {"action_name": "TestSprint", "key": "LeftShift"},
            {"action_name": "TestInteract", "key": "E"}
        ]
        
        for mapping in mappings:
            response = await mcp_client.send_command("create_input_mapping", mapping)
            
            assert response["success"] is True
            assert response.get("action_name") == mapping["action_name"]
            assert response.get("key") == mapping["key"]
    
    async def test_create_input_mapping_gamepad(self, mcp_client: UnrealMCPClient):
        """Test creating gamepad input mappings."""
        gamepad_mappings = [
            {"action_name": "TestGamepadJump", "key": "Gamepad_FaceButton_Bottom"},
            {"action_name": "TestGamepadFire", "key": "Gamepad_RightTrigger"},
            {"action_name": "TestGamepadMenu", "key": "Gamepad_Special_Right"}
        ]
        
        for mapping in gamepad_mappings:
            response = await mcp_client.send_command("create_input_mapping", mapping)
            
            # Gamepad might not be supported in all configurations
            if response["success"]:
                assert response.get("action_name") == mapping["action_name"]
            else:
                print(f"Note: Gamepad mapping {mapping['key']} not supported")
    
    async def test_create_input_mapping_special_keys(self, mcp_client: UnrealMCPClient):
        """Test creating input mappings with special keys."""
        special_keys = [
            {"action_name": "TestEscape", "key": "Escape"},
            {"action_name": "TestTab", "key": "Tab"},
            {"action_name": "TestEnter", "key": "Enter"},
            {"action_name": "TestBackspace", "key": "BackSpace"},
            {"action_name": "TestF1", "key": "F1"}
        ]
        
        for mapping in special_keys:
            response = await mcp_client.send_command("create_input_mapping", mapping)
            
            assert response["success"] is True
            assert response.get("action_name") == mapping["action_name"]
    
    async def test_create_input_mapping_mouse_buttons(self, mcp_client: UnrealMCPClient):
        """Test creating input mappings with mouse buttons."""
        mouse_mappings = [
            {"action_name": "TestLeftClick", "key": "LeftMouseButton"},
            {"action_name": "TestRightClick", "key": "RightMouseButton"},
            {"action_name": "TestMiddleClick", "key": "MiddleMouseButton"},
            {"action_name": "TestMouseX", "key": "MouseX", "scale": 1.0},
            {"action_name": "TestMouseY", "key": "MouseY", "scale": -1.0}
        ]
        
        for mapping in mouse_mappings:
            response = await mcp_client.send_command("create_input_mapping", mapping)
            
            # Mouse axis might be treated differently
            if "Mouse" in mapping["key"] and mapping["key"] in ["MouseX", "MouseY"]:
                # These might need to be axis mappings
                if not response["success"]:
                    # Try without scale
                    del mapping["scale"]
                    response = await mcp_client.send_command("create_input_mapping", mapping)
            
            assert response["success"] is True
    
    async def test_create_input_mapping_duplicate(self, mcp_client: UnrealMCPClient):
        """Test creating duplicate input mappings."""
        # Create initial mapping
        response1 = await mcp_client.send_command("create_input_mapping", {
            "action_name": "TestDuplicate",
            "key": "Q"
        })
        
        assert response1["success"] is True
        
        # Try to create duplicate
        response2 = await mcp_client.send_command("create_input_mapping", {
            "action_name": "TestDuplicate",
            "key": "Q"
        })
        
        # Should either succeed (overwrite) or fail gracefully
        if not response2["success"]:
            assert "error" in response2
        else:
            # If it succeeded, it likely overwrote
            assert response2.get("action_name") == "TestDuplicate"
    
    async def test_create_input_mapping_error_handling(self, mcp_client: UnrealMCPClient):
        """Test error handling for input mapping creation."""
        # Test with invalid key
        response = await mcp_client.send_command("create_input_mapping", {
            "action_name": "TestInvalid",
            "key": "InvalidKey123"
        })
        
        # Should either map to a default or fail gracefully
        if not response["success"]:
            assert "error" in response
            assert len(response["error"]) > 0
    
    async def test_create_input_mapping_empty_name(self, mcp_client: UnrealMCPClient):
        """Test creating input mapping with empty name."""
        response = await mcp_client.send_command("create_input_mapping", {
            "action_name": "",
            "key": "K"
        })
        
        # Should fail with empty name
        assert response["success"] is False
        assert "error" in response
    
    async def test_create_input_mapping_performance(self, mcp_client: UnrealMCPClient):
        """Test performance of creating multiple input mappings."""
        import time
        
        start_time = time.time()
        
        # Create 20 mappings
        for i in range(20):
            response = await mcp_client.send_command("create_input_mapping", {
                "action_name": f"TestPerf_{i}",
                "key": f"F{(i % 12) + 1}"  # F1-F12 keys
            })
            assert response["success"] is True
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (10 seconds for 20 mappings)
        assert elapsed_time < 10.0, f"Input mapping creation took too long: {elapsed_time:.2f}s"
        
        # Calculate average time
        avg_time = elapsed_time / 20
        print(f"Average input mapping creation time: {avg_time*1000:.2f}ms")
    
    async def test_create_input_mapping_combinations(self, mcp_client: UnrealMCPClient):
        """Test creating input mappings with key combinations."""
        combinations = [
            {"action_name": "TestCtrlA", "key": "A", "ctrl": True},
            {"action_name": "TestShiftSpace", "key": "Space", "shift": True},
            {"action_name": "TestAltF4", "key": "F4", "alt": True},
            {"action_name": "TestCtrlShiftS", "key": "S", "ctrl": True, "shift": True},
            {"action_name": "TestCtrlAltDel", "key": "Delete", "ctrl": True, "alt": True}
        ]
        
        for combo in combinations:
            response = await mcp_client.send_command("create_input_mapping", combo)
            
            assert response["success"] is True
            assert response.get("action_name") == combo["action_name"]
            assert response.get("key") == combo["key"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])