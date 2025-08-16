"""
Integration tests for Blueprint node graph manipulation commands.

Tests all blueprint node-related MCP commands for creating and connecting nodes.
"""

import pytest
import asyncio
from typing import Dict, Any
from Python.unreal_mcp_client import UnrealMCPClient


class TestBlueprintNodeCommands:
    """Test suite for blueprint node graph manipulation."""
    
    @pytest.fixture
    async def mcp_client(self):
        """Create an MCP client for testing."""
        client = UnrealMCPClient()
        await client.connect()
        yield client
        await client.disconnect()
    
    @pytest.fixture
    async def test_blueprint(self, mcp_client: UnrealMCPClient):
        """Create a test blueprint for node operations."""
        response = await mcp_client.send_command("create_blueprint", {
            "blueprint_name": "BP_NodeTest",
            "parent_class": "/Script/Engine.Actor"
        })
        
        yield response["blueprint_path"]
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": response["blueprint_path"]
        })
    
    async def test_add_blueprint_event_node(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test adding event nodes to blueprint."""
        response = await mcp_client.send_command("add_blueprint_event_node", {
            "blueprint_path": test_blueprint,
            "event_name": "BeginPlay"
        })
        
        assert response["success"] is True
        assert "node_id" in response
        assert response.get("event_name") == "BeginPlay"
    
    async def test_add_blueprint_function_node(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test adding function nodes to blueprint."""
        response = await mcp_client.send_command("add_blueprint_function_node", {
            "blueprint_path": test_blueprint,
            "function_name": "PrintString",
            "target_class": "/Script/Engine.KismetSystemLibrary"
        })
        
        assert response["success"] is True
        assert "node_id" in response
    
    async def test_add_blueprint_variable(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test adding variables to blueprint."""
        response = await mcp_client.send_command("add_blueprint_variable", {
            "blueprint_path": test_blueprint,
            "variable_name": "TestFloat",
            "variable_type": "float"
        })
        
        assert response["success"] is True
        assert response.get("variable_name") == "TestFloat"
    
    async def test_add_blueprint_self_reference(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test adding self reference node."""
        response = await mcp_client.send_command("add_blueprint_self_reference", {
            "blueprint_path": test_blueprint
        })
        
        assert response["success"] is True
        assert "node_id" in response
    
    async def test_add_blueprint_get_component_node(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test adding get component node to blueprint."""
        # First add a component to the blueprint
        await mcp_client.send_command("add_component_to_blueprint", {
            "blueprint_path": test_blueprint,
            "component_name": "TestMesh",
            "component_class": "StaticMeshComponent"
        })
        
        # Now add a get component node
        response = await mcp_client.send_command("add_blueprint_get_component_node", {
            "blueprint_path": test_blueprint,
            "component_name": "TestMesh"
        })
        
        assert response["success"] is True
        assert "node_id" in response
        assert response.get("component_name") == "TestMesh"
    
    async def test_add_blueprint_get_self_component_reference(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test adding self component reference node."""
        # Add a component first
        await mcp_client.send_command("add_component_to_blueprint", {
            "blueprint_path": test_blueprint,
            "component_name": "TestComponent",
            "component_class": "SceneComponent"
        })
        
        response = await mcp_client.send_command("add_blueprint_get_self_component_reference", {
            "blueprint_path": test_blueprint,
            "component_name": "TestComponent"
        })
        
        assert response["success"] is True
        assert "node_id" in response
    
    async def test_add_blueprint_input_action_node(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test adding input action node."""
        # First create an input mapping
        await mcp_client.send_command("create_input_mapping", {
            "action_name": "TestAction",
            "key": "Space"
        })
        
        response = await mcp_client.send_command("add_blueprint_input_action_node", {
            "blueprint_path": test_blueprint,
            "action_name": "TestAction"
        })
        
        assert response["success"] is True
        assert "node_id" in response
    
    async def test_connect_blueprint_nodes(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test connecting blueprint nodes."""
        # Create two nodes to connect
        event_response = await mcp_client.send_command("add_blueprint_event_node", {
            "blueprint_path": test_blueprint,
            "event_name": "BeginPlay"
        })
        
        function_response = await mcp_client.send_command("add_blueprint_function_node", {
            "blueprint_path": test_blueprint,
            "function_name": "PrintString",
            "target_class": "/Script/Engine.KismetSystemLibrary"
        })
        
        # Connect the nodes
        response = await mcp_client.send_command("connect_blueprint_nodes", {
            "blueprint_path": test_blueprint,
            "source_node_id": event_response["node_id"],
            "source_pin": "exec",
            "target_node_id": function_response["node_id"],
            "target_pin": "exec"
        })
        
        assert response["success"] is True
        assert response.get("connected") is True
    
    async def test_find_blueprint_nodes(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test finding nodes in blueprint."""
        # Add some nodes
        await mcp_client.send_command("add_blueprint_event_node", {
            "blueprint_path": test_blueprint,
            "event_name": "BeginPlay"
        })
        
        await mcp_client.send_command("add_blueprint_event_node", {
            "blueprint_path": test_blueprint,
            "event_name": "Tick"
        })
        
        # Find nodes
        response = await mcp_client.send_command("find_blueprint_nodes", {
            "blueprint_path": test_blueprint,
            "node_type": "Event"
        })
        
        assert response["success"] is True
        assert "nodes" in response
        assert len(response["nodes"]) >= 2
    
    async def test_complex_node_graph(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test creating a complex node graph."""
        # Add component
        await mcp_client.send_command("add_component_to_blueprint", {
            "blueprint_path": test_blueprint,
            "component_name": "RotatingMesh",
            "component_class": "StaticMeshComponent"
        })
        
        # Add variable for rotation speed
        await mcp_client.send_command("add_blueprint_variable", {
            "blueprint_path": test_blueprint,
            "variable_name": "RotationSpeed",
            "variable_type": "float",
            "default_value": "90.0"
        })
        
        # Add tick event
        tick_response = await mcp_client.send_command("add_blueprint_event_node", {
            "blueprint_path": test_blueprint,
            "event_name": "Tick"
        })
        
        # Add get component node
        component_response = await mcp_client.send_command("add_blueprint_get_component_node", {
            "blueprint_path": test_blueprint,
            "component_name": "RotatingMesh"
        })
        
        # Add rotation function
        rotate_response = await mcp_client.send_command("add_blueprint_function_node", {
            "blueprint_path": test_blueprint,
            "function_name": "AddRelativeRotation",
            "target_class": "/Script/Engine.SceneComponent"
        })
        
        # Connect nodes
        await mcp_client.send_command("connect_blueprint_nodes", {
            "blueprint_path": test_blueprint,
            "source_node_id": tick_response["node_id"],
            "source_pin": "exec",
            "target_node_id": rotate_response["node_id"],
            "target_pin": "exec"
        })
        
        await mcp_client.send_command("connect_blueprint_nodes", {
            "blueprint_path": test_blueprint,
            "source_node_id": component_response["node_id"],
            "source_pin": "output",
            "target_node_id": rotate_response["node_id"],
            "target_pin": "target"
        })
        
        # Compile blueprint
        compile_response = await mcp_client.send_command("compile_blueprint", {
            "blueprint_path": test_blueprint
        })
        
        assert compile_response["success"] is True
    
    async def test_node_error_handling(self, mcp_client: UnrealMCPClient):
        """Test error handling for node operations."""
        # Test with non-existent blueprint
        response = await mcp_client.send_command("add_blueprint_event_node", {
            "blueprint_path": "/Game/NonExistent/Blueprint",
            "event_name": "BeginPlay"
        })
        
        assert response["success"] is False
        assert "error" in response
        
        # Test invalid node connection
        bp_response = await mcp_client.send_command("create_blueprint", {
            "blueprint_name": "BP_ErrorTest",
            "parent_class": "/Script/Engine.Actor"
        })
        
        blueprint_path = bp_response["blueprint_path"]
        
        response = await mcp_client.send_command("connect_blueprint_nodes", {
            "blueprint_path": blueprint_path,
            "source_node_id": "invalid_node_1",
            "source_pin": "exec",
            "target_node_id": "invalid_node_2",
            "target_pin": "exec"
        })
        
        assert response["success"] is False
        assert "error" in response
        
        # Clean up
        await mcp_client.send_command("delete_asset", {
            "asset_path": blueprint_path
        })
    
    async def test_node_performance(self, mcp_client: UnrealMCPClient, test_blueprint: str):
        """Test performance of node operations."""
        import time
        
        start_time = time.time()
        
        # Add multiple nodes
        nodes = []
        for i in range(10):
            response = await mcp_client.send_command("add_blueprint_function_node", {
                "blueprint_path": test_blueprint,
                "function_name": "PrintString",
                "target_class": "/Script/Engine.KismetSystemLibrary"
            })
            nodes.append(response["node_id"])
        
        # Create a chain of connections
        event_response = await mcp_client.send_command("add_blueprint_event_node", {
            "blueprint_path": test_blueprint,
            "event_name": "BeginPlay"
        })
        
        prev_node = event_response["node_id"]
        for node_id in nodes:
            await mcp_client.send_command("connect_blueprint_nodes", {
                "blueprint_path": test_blueprint,
                "source_node_id": prev_node,
                "source_pin": "exec",
                "target_node_id": node_id,
                "target_pin": "exec"
            })
            prev_node = node_id
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (20 seconds for 21 operations)
        assert elapsed_time < 20.0, f"Node operations took too long: {elapsed_time:.2f}s"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])