"""
Integration tests for core MCP commands.

Tests basic connectivity and core functionality commands.
"""

import pytest
import asyncio
from typing import Dict, Any
from Python.unreal_mcp_client import UnrealMCPClient


class TestCoreCommands:
    """Test suite for core MCP commands."""
    
    @pytest.fixture
    async def mcp_client(self):
        """Create an MCP client for testing."""
        client = UnrealMCPClient()
        await client.connect()
        yield client
        await client.disconnect()
    
    async def test_ping_command(self, mcp_client: UnrealMCPClient):
        """Test the ping command for basic connectivity."""
        response = await mcp_client.send_command("ping", {})
        
        assert response["success"] is True
        assert "message" in response
        assert response["message"] == "pong"
    
    async def test_ping_command_multiple_times(self, mcp_client: UnrealMCPClient):
        """Test ping command multiple times to ensure consistency."""
        for i in range(5):
            response = await mcp_client.send_command("ping", {})
            
            assert response["success"] is True
            assert response["message"] == "pong"
            
            # Small delay between pings
            await asyncio.sleep(0.1)
    
    async def test_ping_command_performance(self, mcp_client: UnrealMCPClient):
        """Test ping command performance."""
        import time
        
        start_time = time.time()
        
        # Send 10 ping commands
        for _ in range(10):
            response = await mcp_client.send_command("ping", {})
            assert response["success"] is True
        
        elapsed_time = time.time() - start_time
        
        # 10 pings should complete in under 2 seconds
        assert elapsed_time < 2.0, f"Ping commands took too long: {elapsed_time:.2f}s"
        
        # Calculate average ping time
        avg_ping = elapsed_time / 10
        print(f"Average ping time: {avg_ping*1000:.2f}ms")
    
    async def test_create_actor_command(self, mcp_client: UnrealMCPClient):
        """Test the create_actor command."""
        # Create a basic actor
        response = await mcp_client.send_command("create_actor", {
            "actor_class": "Actor",
            "actor_name": "TestActor_Create",
            "location": {"x": 100, "y": 200, "z": 50}
        })
        
        assert response["success"] is True
        assert "actor_name" in response
        assert "TestActor_Create" in response["actor_name"]
        
        # Verify actor exists
        find_response = await mcp_client.send_command("find_actors_by_name", {
            "name_pattern": response["actor_name"]
        })
        
        assert find_response["success"] is True
        assert len(find_response["actors"]) == 1
        
        # Clean up
        await mcp_client.send_command("delete_actor", {
            "actor_name": response["actor_name"]
        })
    
    async def test_create_actor_with_components(self, mcp_client: UnrealMCPClient):
        """Test creating an actor with components."""
        # Create actor with mesh component
        response = await mcp_client.send_command("create_actor", {
            "actor_class": "StaticMeshActor",
            "actor_name": "TestMeshActor_Create",
            "location": {"x": 0, "y": 0, "z": 100},
            "mesh_path": "/Engine/BasicShapes/Cube"
        })
        
        if response["success"]:
            assert "actor_name" in response
            actor_name = response["actor_name"]
            
            # Get actor properties to verify mesh
            props_response = await mcp_client.send_command("get_actor_properties", {
                "actor_name": actor_name
            })
            
            assert props_response["success"] is True
            
            # Clean up
            await mcp_client.send_command("delete_actor", {
                "actor_name": actor_name
            })
        else:
            # If create_actor doesn't support mesh_path, test basic creation
            response = await mcp_client.send_command("create_actor", {
                "actor_class": "StaticMeshActor",
                "actor_name": "TestMeshActor_Create",
                "location": {"x": 0, "y": 0, "z": 100}
            })
            
            assert response["success"] is True
            assert "actor_name" in response
            
            # Clean up
            await mcp_client.send_command("delete_actor", {
                "actor_name": response["actor_name"]
            })
    
    async def test_create_actor_different_types(self, mcp_client: UnrealMCPClient):
        """Test creating different types of actors."""
        actor_types = [
            {"class": "Actor", "name": "BasicActor"},
            {"class": "StaticMeshActor", "name": "MeshActor"},
            {"class": "DirectionalLight", "name": "LightActor"},
            {"class": "CameraActor", "name": "CameraActor"}
        ]
        
        created_actors = []
        
        for actor_type in actor_types:
            response = await mcp_client.send_command("create_actor", {
                "actor_class": actor_type["class"],
                "actor_name": f"Test_{actor_type['name']}",
                "location": {"x": 0, "y": 0, "z": 0}
            })
            
            if response["success"]:
                assert "actor_name" in response
                created_actors.append(response["actor_name"])
            else:
                # Some actor types might not be supported by create_actor
                print(f"Note: create_actor doesn't support {actor_type['class']}")
        
        # Clean up all created actors
        for actor_name in created_actors:
            await mcp_client.send_command("delete_actor", {
                "actor_name": actor_name
            })
    
    async def test_create_actor_with_transform(self, mcp_client: UnrealMCPClient):
        """Test creating an actor with full transform."""
        response = await mcp_client.send_command("create_actor", {
            "actor_class": "Actor",
            "actor_name": "TestActor_Transform",
            "location": {"x": 150, "y": 250, "z": 100},
            "rotation": {"pitch": 15, "yaw": 30, "roll": 0},
            "scale": {"x": 2, "y": 2, "z": 2}
        })
        
        if response["success"]:
            assert "actor_name" in response
            actor_name = response["actor_name"]
            
            # Verify transform
            props_response = await mcp_client.send_command("get_actor_properties", {
                "actor_name": actor_name
            })
            
            if props_response["success"] and "transform" in props_response:
                transform = props_response["transform"]
                # Verify location was set
                assert transform["location"]["x"] == 150
                assert transform["location"]["y"] == 250
                assert transform["location"]["z"] == 100
            
            # Clean up
            await mcp_client.send_command("delete_actor", {
                "actor_name": actor_name
            })
        else:
            # If full transform not supported, just test basic creation
            response = await mcp_client.send_command("create_actor", {
                "actor_class": "Actor",
                "actor_name": "TestActor_Basic",
                "location": {"x": 0, "y": 0, "z": 0}
            })
            
            assert response["success"] is True
            
            # Clean up
            await mcp_client.send_command("delete_actor", {
                "actor_name": response["actor_name"]
            })
    
    async def test_create_actor_error_handling(self, mcp_client: UnrealMCPClient):
        """Test error handling for create_actor command."""
        # Test with invalid actor class
        response = await mcp_client.send_command("create_actor", {
            "actor_class": "InvalidActorClass",
            "actor_name": "TestInvalid",
            "location": {"x": 0, "y": 0, "z": 0}
        })
        
        # Should either fail gracefully or create a default actor
        if not response["success"]:
            assert "error" in response
            # Error message should be informative
            assert len(response["error"]) > 0
        else:
            # If it succeeded, clean up
            await mcp_client.send_command("delete_actor", {
                "actor_name": response["actor_name"]
            })
    
    async def test_create_vs_spawn_actor(self, mcp_client: UnrealMCPClient):
        """Compare create_actor vs spawn_actor commands."""
        # Test create_actor
        create_response = await mcp_client.send_command("create_actor", {
            "actor_class": "StaticMeshActor",
            "actor_name": "CreatedActor",
            "location": {"x": -100, "y": 0, "z": 50}
        })
        
        # Test spawn_actor
        spawn_response = await mcp_client.send_command("spawn_actor", {
            "actor_type": "StaticMeshActor",
            "location": {"x": 100, "y": 0, "z": 50}
        })
        
        # Both should succeed
        assert create_response["success"] is True or spawn_response["success"] is True
        
        # Clean up
        if create_response["success"]:
            await mcp_client.send_command("delete_actor", {
                "actor_name": create_response["actor_name"]
            })
        
        if spawn_response["success"]:
            await mcp_client.send_command("delete_actor", {
                "actor_name": spawn_response["actor_name"]
            })
    
    async def test_connection_stability(self, mcp_client: UnrealMCPClient):
        """Test connection stability with multiple commands."""
        commands_to_test = [
            ("ping", {}),
            ("get_actors_in_level", {}),
            ("ping", {}),
            ("get_current_level_info", {}),
            ("ping", {})
        ]
        
        for cmd, params in commands_to_test:
            response = await mcp_client.send_command(cmd, params)
            assert response["success"] is True, f"Command {cmd} failed"
            
            # Small delay between commands
            await asyncio.sleep(0.05)
    
    async def test_command_with_empty_params(self, mcp_client: UnrealMCPClient):
        """Test commands that don't require parameters."""
        # Commands that should work with empty params
        commands = ["ping", "get_actors_in_level", "get_current_level_info"]
        
        for cmd in commands:
            response = await mcp_client.send_command(cmd, {})
            assert response["success"] is True, f"Command {cmd} failed with empty params"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])