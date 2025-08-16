"""
Integration tests for screenshot verification functionality.

Tests the ability to take and verify screenshots throughout the testing process.
"""

import pytest
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from Python.unreal_mcp_client import UnrealMCPClient


class TestScreenshotVerification:
    """Test suite for screenshot capture and verification."""
    
    @pytest.fixture
    async def mcp_client(self):
        """Create an MCP client for testing."""
        client = UnrealMCPClient()
        await client.connect()
        yield client
        await client.disconnect()
    
    @pytest.fixture
    def screenshot_dir(self):
        """Create a directory for test screenshots."""
        test_dir = Path("Python/tests/test_screenshots")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = test_dir / f"test_run_{timestamp}"
        run_dir.mkdir(exist_ok=True)
        
        yield run_dir
        
        # Cleanup old screenshots (keep last 5 runs)
        all_runs = sorted([d for d in test_dir.iterdir() if d.is_dir()])
        if len(all_runs) > 5:
            for old_run in all_runs[:-5]:
                import shutil
                shutil.rmtree(old_run)
    
    async def test_basic_screenshot(self, mcp_client: UnrealMCPClient, screenshot_dir: Path):
        """Test basic screenshot functionality."""
        # Take a screenshot
        screenshot_path = str(screenshot_dir / "test_basic.png")
        response = await mcp_client.send_command("take_screenshot", {
            "file_path": screenshot_path
        })
        
        assert response["success"] is True
        assert "screenshot_path" in response
        
        # Verify file exists
        assert Path(response["screenshot_path"]).exists()
        
        # Verify file size (should be > 100KB for a real screenshot)
        file_size = Path(response["screenshot_path"]).stat().st_size
        assert file_size > 100_000, f"Screenshot too small: {file_size} bytes"
    
    async def test_screenshot_with_actor_spawn(self, mcp_client: UnrealMCPClient, screenshot_dir: Path):
        """Test screenshot after spawning an actor."""
        # Spawn a cube
        spawn_response = await mcp_client.send_command("spawn_actor", {
            "actor_type": "StaticMeshActor",
            "location": {"x": 0, "y": 0, "z": 100},
            "mesh_path": "/Engine/BasicShapes/Cube"
        })
        
        assert spawn_response["success"] is True
        actor_name = spawn_response["actor_name"]
        
        # Focus on the actor
        await mcp_client.send_command("focus_viewport", {
            "actor_name": actor_name,
            "distance": 500
        })
        
        # Take screenshot
        screenshot_path = str(screenshot_dir / "test_cube_spawn.png")
        screenshot_response = await mcp_client.send_command("take_screenshot", {
            "file_path": screenshot_path
        })
        
        assert screenshot_response["success"] is True
        assert Path(screenshot_response["screenshot_path"]).exists()
        
        # Clean up
        await mcp_client.send_command("delete_actor", {
            "actor_name": actor_name
        })
    
    async def test_screenshot_sequence(self, mcp_client: UnrealMCPClient, screenshot_dir: Path):
        """Test taking multiple screenshots in sequence."""
        screenshots = []
        
        # Create multiple actors at different positions
        actors = []
        positions = [
            {"x": 0, "y": 0, "z": 100},
            {"x": 200, "y": 0, "z": 100},
            {"x": -200, "y": 0, "z": 100},
            {"x": 0, "y": 200, "z": 100},
            {"x": 0, "y": -200, "z": 100}
        ]
        
        for i, pos in enumerate(positions):
            # Spawn actor
            response = await mcp_client.send_command("spawn_actor", {
                "actor_type": "StaticMeshActor",
                "location": pos,
                "mesh_path": "/Engine/BasicShapes/Sphere"
            })
            actors.append(response["actor_name"])
            
            # Focus and screenshot
            await mcp_client.send_command("focus_viewport", {
                "actor_name": response["actor_name"],
                "distance": 300
            })
            
            screenshot_path = str(screenshot_dir / f"sequence_{i:02d}.png")
            screenshot_response = await mcp_client.send_command("take_screenshot", {
                "file_path": screenshot_path
            })
            
            screenshots.append(screenshot_response["screenshot_path"])
            
            # Small delay between screenshots
            await asyncio.sleep(0.5)
        
        # Verify all screenshots exist
        for path in screenshots:
            assert Path(path).exists()
            assert Path(path).stat().st_size > 100_000
        
        # Clean up actors
        for actor_name in actors:
            await mcp_client.send_command("delete_actor", {
                "actor_name": actor_name
            })
    
    async def test_screenshot_with_blueprint(self, mcp_client: UnrealMCPClient, screenshot_dir: Path):
        """Test screenshot after creating and spawning a blueprint."""
        # Create a simple blueprint
        bp_response = await mcp_client.send_command("create_blueprint", {
            "blueprint_name": "BP_ScreenshotTest",
            "parent_class": "/Script/Engine.Actor"
        })
        
        assert bp_response["success"] is True
        
        # Add a mesh component
        await mcp_client.send_command("add_component_to_blueprint", {
            "blueprint_path": bp_response["blueprint_path"],
            "component_name": "TestMesh",
            "component_class": "StaticMeshComponent"
        })
        
        # Set the mesh
        await mcp_client.send_command("set_component_property", {
            "blueprint_path": bp_response["blueprint_path"],
            "component_name": "TestMesh",
            "property_name": "StaticMesh",
            "property_value": "/Engine/BasicShapes/Cylinder"
        })
        
        # Compile blueprint
        await mcp_client.send_command("compile_blueprint", {
            "blueprint_path": bp_response["blueprint_path"]
        })
        
        # Spawn the blueprint
        spawn_response = await mcp_client.send_command("spawn_blueprint_actor", {
            "blueprint_path": bp_response["blueprint_path"],
            "location": {"x": 0, "y": 0, "z": 200},
            "rotation": {"pitch": 0, "yaw": 45, "roll": 0}
        })
        
        actor_name = spawn_response["actor_name"]
        
        # Focus and screenshot
        await mcp_client.send_command("focus_viewport", {
            "actor_name": actor_name,
            "distance": 400
        })
        
        screenshot_path = str(screenshot_dir / "test_blueprint_spawn.png")
        screenshot_response = await mcp_client.send_command("take_screenshot", {
            "file_path": screenshot_path
        })
        
        assert screenshot_response["success"] is True
        assert Path(screenshot_response["screenshot_path"]).exists()
        
        # Clean up
        await mcp_client.send_command("delete_actor", {
            "actor_name": actor_name
        })
        await mcp_client.send_command("delete_asset", {
            "asset_path": bp_response["blueprint_path"]
        })
    
    async def test_screenshot_with_level_change(self, mcp_client: UnrealMCPClient, screenshot_dir: Path):
        """Test screenshot after level operations."""
        # Create a new level
        level_response = await mcp_client.send_command("create_level", {
            "level_name": "ScreenshotTestLevel",
            "level_path": "/Game/Maps/Test"
        })
        
        if level_response["success"]:
            # Load the level
            await mcp_client.send_command("load_level", {
                "level_path": level_response["level_path"]
            })
            
            # Add some actors to the new level
            actors = []
            for i in range(3):
                response = await mcp_client.send_command("spawn_actor", {
                    "actor_type": "StaticMeshActor",
                    "location": {"x": i * 200 - 200, "y": 0, "z": 100},
                    "mesh_path": "/Engine/BasicShapes/Cone"
                })
                actors.append(response["actor_name"])
            
            # Take overview screenshot
            screenshot_path = str(screenshot_dir / "test_level_overview.png")
            screenshot_response = await mcp_client.send_command("take_screenshot", {
                "file_path": screenshot_path
            })
            
            assert screenshot_response["success"] is True
            assert Path(screenshot_response["screenshot_path"]).exists()
            
            # Clean up actors
            for actor_name in actors:
                await mcp_client.send_command("delete_actor", {
                    "actor_name": actor_name
                })
    
    async def test_screenshot_error_handling(self, mcp_client: UnrealMCPClient):
        """Test screenshot error handling."""
        # Test with invalid path
        response = await mcp_client.send_command("take_screenshot", {
            "file_path": "/invalid/path/that/does/not/exist/screenshot.png"
        })
        
        # Should handle gracefully
        if not response["success"]:
            assert "error" in response
            # Error message should be informative
            assert len(response["error"]) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])