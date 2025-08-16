"""
Integration tests for UMG (Unreal Motion Graphics) widget commands.

Tests all UMG-related MCP commands for creating and managing UI widgets.
"""

import pytest
import asyncio
import json
from pathlib import Path
from typing import Dict, Any
from Python.unreal_mcp_client import UnrealMCPClient


class TestUMGCommands:
    """Test suite for UMG widget commands."""
    
    @pytest.fixture
    async def mcp_client(self):
        """Create an MCP client for testing."""
        client = UnrealMCPClient()
        await client.connect()
        yield client
        await client.disconnect()
    
    @pytest.fixture
    def test_widget_path(self):
        """Provide a test widget blueprint path."""
        return "/Game/Test/Widgets/WBP_TestWidget"
    
    async def test_create_umg_widget_blueprint(self, mcp_client: UnrealMCPClient, test_widget_path: str):
        """Test creating a UMG widget blueprint."""
        response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_TestWidget",
            "widget_path": "/Game/Test/Widgets"
        })
        
        assert response["success"] is True
        assert "widget_path" in response
        assert response["widget_path"] == test_widget_path
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": test_widget_path
        })
    
    async def test_add_text_block_to_widget(self, mcp_client: UnrealMCPClient, test_widget_path: str):
        """Test adding a text block to a widget."""
        # Create widget first
        create_response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_TextTest",
            "widget_path": "/Game/Test/Widgets"
        })
        
        widget_path = create_response["widget_path"]
        
        # Add text block
        response = await mcp_client.send_command("add_text_block_to_widget", {
            "widget_path": widget_path,
            "text_name": "TestText",
            "default_text": "Hello UMG!",
            "position": {"x": 100, "y": 100},
            "size": {"x": 200, "y": 50}
        })
        
        assert response["success"] is True
        assert response.get("text_name") == "TestText"
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": widget_path
        })
    
    async def test_add_button_to_widget(self, mcp_client: UnrealMCPClient, test_widget_path: str):
        """Test adding a button to a widget."""
        # Create widget
        create_response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_ButtonTest",
            "widget_path": "/Game/Test/Widgets"
        })
        
        widget_path = create_response["widget_path"]
        
        # Add button
        response = await mcp_client.send_command("add_button_to_widget", {
            "widget_path": widget_path,
            "button_name": "TestButton",
            "button_text": "Click Me!",
            "position": {"x": 150, "y": 200},
            "size": {"x": 150, "y": 40}
        })
        
        assert response["success"] is True
        assert response.get("button_name") == "TestButton"
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": widget_path
        })
    
    async def test_bind_widget_event(self, mcp_client: UnrealMCPClient):
        """Test binding events to widget elements."""
        # Create widget with button
        create_response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_EventTest",
            "widget_path": "/Game/Test/Widgets"
        })
        
        widget_path = create_response["widget_path"]
        
        # Add button
        await mcp_client.send_command("add_button_to_widget", {
            "widget_path": widget_path,
            "button_name": "EventButton",
            "button_text": "Event Test",
            "position": {"x": 100, "y": 100},
            "size": {"x": 100, "y": 30}
        })
        
        # Bind click event
        response = await mcp_client.send_command("bind_widget_event", {
            "widget_path": widget_path,
            "widget_name": "EventButton",
            "event_type": "OnClicked",
            "function_name": "OnEventButtonClicked"
        })
        
        assert response["success"] is True
        assert "function_name" in response
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": widget_path
        })
    
    async def test_set_text_block_binding(self, mcp_client: UnrealMCPClient):
        """Test setting data binding for text blocks."""
        # Create widget
        create_response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_BindingTest",
            "widget_path": "/Game/Test/Widgets"
        })
        
        widget_path = create_response["widget_path"]
        
        # Add text block
        await mcp_client.send_command("add_text_block_to_widget", {
            "widget_path": widget_path,
            "text_name": "BoundText",
            "default_text": "Initial",
            "position": {"x": 50, "y": 50},
            "size": {"x": 300, "y": 30}
        })
        
        # Set binding
        response = await mcp_client.send_command("set_text_block_binding", {
            "widget_path": widget_path,
            "text_name": "BoundText",
            "binding_function": "GetDynamicText"
        })
        
        assert response["success"] is True
        assert "binding_function" in response
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": widget_path
        })
    
    async def test_add_widget_to_viewport(self, mcp_client: UnrealMCPClient):
        """Test adding a widget to the viewport."""
        # Create widget
        create_response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_ViewportTest",
            "widget_path": "/Game/Test/Widgets"
        })
        
        widget_path = create_response["widget_path"]
        
        # Add some content
        await mcp_client.send_command("add_text_block_to_widget", {
            "widget_path": widget_path,
            "text_name": "ViewportText",
            "default_text": "Viewport Widget Test",
            "position": {"x": 100, "y": 100},
            "size": {"x": 400, "y": 100}
        })
        
        # Add to viewport
        response = await mcp_client.send_command("add_widget_to_viewport", {
            "widget_path": widget_path,
            "z_order": 0
        })
        
        assert response["success"] is True
        assert "instance_name" in response
        
        # Note: In a real scenario, we'd want to remove the widget from viewport
        # but that command might not be implemented yet
        
        # Clean up asset
        await mcp_client.send_command("delete_asset", {
            "asset_path": widget_path
        })
    
    async def test_complex_widget_creation(self, mcp_client: UnrealMCPClient):
        """Test creating a complex widget with multiple elements."""
        # Create main widget
        create_response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_ComplexUI",
            "widget_path": "/Game/Test/Widgets"
        })
        
        widget_path = create_response["widget_path"]
        
        # Add title text
        await mcp_client.send_command("add_text_block_to_widget", {
            "widget_path": widget_path,
            "text_name": "TitleText",
            "default_text": "Complex UI Test",
            "position": {"x": 200, "y": 50},
            "size": {"x": 400, "y": 60}
        })
        
        # Add multiple buttons
        button_configs = [
            {"name": "StartButton", "text": "Start", "x": 100, "y": 150},
            {"name": "OptionsButton", "text": "Options", "x": 300, "y": 150},
            {"name": "QuitButton", "text": "Quit", "x": 500, "y": 150}
        ]
        
        for config in button_configs:
            response = await mcp_client.send_command("add_button_to_widget", {
                "widget_path": widget_path,
                "button_name": config["name"],
                "button_text": config["text"],
                "position": {"x": config["x"], "y": config["y"]},
                "size": {"x": 150, "y": 40}
            })
            assert response["success"] is True
        
        # Add status text
        await mcp_client.send_command("add_text_block_to_widget", {
            "widget_path": widget_path,
            "text_name": "StatusText",
            "default_text": "Ready",
            "position": {"x": 200, "y": 250},
            "size": {"x": 400, "y": 30}
        })
        
        # Bind events to buttons
        for button_name in ["StartButton", "OptionsButton", "QuitButton"]:
            response = await mcp_client.send_command("bind_widget_event", {
                "widget_path": widget_path,
                "widget_name": button_name,
                "event_type": "OnClicked",
                "function_name": f"On{button_name}Clicked"
            })
            assert response["success"] is True
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": widget_path
        })
    
    async def test_widget_error_handling(self, mcp_client: UnrealMCPClient):
        """Test error handling for widget commands."""
        # Test adding element to non-existent widget
        response = await mcp_client.send_command("add_text_block_to_widget", {
            "widget_path": "/Game/NonExistent/Widget",
            "text_name": "TestText",
            "default_text": "Test",
            "position": {"x": 0, "y": 0},
            "size": {"x": 100, "y": 30}
        })
        
        assert response["success"] is False
        assert "error" in response
        
        # Test invalid event binding
        create_response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_ErrorTest",
            "widget_path": "/Game/Test/Widgets"
        })
        
        widget_path = create_response["widget_path"]
        
        # Try to bind event to non-existent element
        response = await mcp_client.send_command("bind_widget_event", {
            "widget_path": widget_path,
            "widget_name": "NonExistentButton",
            "event_type": "OnClicked",
            "function_name": "TestFunction"
        })
        
        assert response["success"] is False
        assert "error" in response
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": widget_path
        })
    
    async def test_widget_performance(self, mcp_client: UnrealMCPClient):
        """Test performance of widget operations."""
        import time
        
        # Create widget
        create_response = await mcp_client.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_PerfTest",
            "widget_path": "/Game/Test/Widgets"
        })
        
        widget_path = create_response["widget_path"]
        
        # Measure time to add multiple elements
        start_time = time.time()
        
        # Add 10 text blocks
        for i in range(10):
            await mcp_client.send_command("add_text_block_to_widget", {
                "widget_path": widget_path,
                "text_name": f"Text_{i}",
                "default_text": f"Text Block {i}",
                "position": {"x": 50, "y": 50 + i * 35},
                "size": {"x": 200, "y": 30}
            })
        
        # Add 5 buttons
        for i in range(5):
            await mcp_client.send_command("add_button_to_widget", {
                "widget_path": widget_path,
                "button_name": f"Button_{i}",
                "button_text": f"Button {i}",
                "position": {"x": 300, "y": 50 + i * 50},
                "size": {"x": 100, "y": 40}
            })
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (15 seconds for 15 operations)
        assert elapsed_time < 15.0, f"Widget operations took too long: {elapsed_time:.2f}s"
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": widget_path
        })


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])