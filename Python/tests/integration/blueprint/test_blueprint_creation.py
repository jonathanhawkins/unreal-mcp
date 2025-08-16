"""
Integration tests for blueprint creation and management MCP tools.

Tests the complete workflow of creating, modifying, compiling, and using
blueprints in Unreal Engine through the MCP interface.
"""

import pytest
import time

from ...fixtures.common_fixtures import wait_for_compilation, assert_blueprint_compiled
from ...data.test_data import get_blueprint_data

@pytest.mark.integration
@pytest.mark.blueprints
@pytest.mark.requires_unreal
class TestBlueprintCreation:
    """Test blueprint creation and management functionality."""
    
    def test_create_simple_blueprint(self, test_framework, clean_environment):
        """Test creating a simple actor blueprint."""
        blueprint_data = get_blueprint_data("simple_actor")
        
        with test_framework.test_connection() as conn:
            # Create the blueprint
            response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            
            test_framework.assert_response_success(response, "Failed to create blueprint")
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_data.name
            })
            # Don't assert success as delete_blueprint might not be implemented
    
    def test_create_blueprint_with_components(self, test_framework, clean_environment):
        """Test creating a blueprint and adding components."""
        blueprint_data = get_blueprint_data("simple_actor")
        
        with test_framework.test_connection() as conn:
            # Create the blueprint
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            test_framework.assert_response_success(create_response, "Failed to create blueprint")
            
            # Add components
            for component in blueprint_data.components:
                comp_response = conn.send_command("add_component_to_blueprint", {
                    "blueprint_name": blueprint_data.name,
                    "component_type": component.type,
                    "component_name": component.name
                })
                test_framework.assert_response_success(comp_response, f"Failed to add component {component.name}")
            
            # Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile blueprint")
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_data.name
            })
    
    def test_blueprint_with_variables(self, test_framework, clean_environment):
        """Test creating a blueprint with variables."""
        blueprint_data = get_blueprint_data("simple_actor")
        
        with test_framework.test_connection() as conn:
            # Create the blueprint
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            test_framework.assert_response_success(create_response, "Failed to create blueprint")
            
            # Add variables
            for variable in blueprint_data.variables:
                var_response = conn.send_command("add_blueprint_variable", {
                    "blueprint_name": blueprint_data.name,
                    "variable_name": variable["name"],
                    "variable_type": variable["type"],
                    "default_value": variable.get("default_value")
                })
                test_framework.assert_response_success(var_response, f"Failed to add variable {variable['name']}")
            
            # Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile blueprint")
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_data.name
            })
    
    def test_pawn_blueprint_creation(self, test_framework, clean_environment):
        """Test creating a pawn blueprint with movement and camera."""
        blueprint_data = get_blueprint_data("pawn_with_input")
        
        with test_framework.test_connection() as conn:
            # Create the pawn blueprint
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            test_framework.assert_response_success(create_response, "Failed to create pawn blueprint")
            
            # Add mesh component
            mesh_response = conn.send_command("add_component_to_blueprint", {
                "blueprint_name": blueprint_data.name,
                "component_type": "StaticMeshComponent",
                "component_name": "Mesh"
            })
            test_framework.assert_response_success(mesh_response, "Failed to add mesh component")
            
            # Add camera component
            camera_response = conn.send_command("add_component_to_blueprint", {
                "blueprint_name": blueprint_data.name,
                "component_type": "CameraComponent",
                "component_name": "Camera"
            })
            test_framework.assert_response_success(camera_response, "Failed to add camera component")
            
            # Add movement component
            movement_response = conn.send_command("add_component_to_blueprint", {
                "blueprint_name": blueprint_data.name,
                "component_type": "FloatingPawnMovement",
                "component_name": "MovementComponent"
            })
            test_framework.assert_response_success(movement_response, "Failed to add movement component")
            
            # Set pawn properties
            pawn_props_response = conn.send_command("set_pawn_properties", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(pawn_props_response, "Failed to set pawn properties")
            
            # Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile pawn blueprint")
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_data.name
            })
    
    def test_spawn_blueprint_actor(self, test_framework, clean_environment):
        """Test spawning an actor from a blueprint."""
        blueprint_data = get_blueprint_data("simple_actor")
        actor_name = f"{blueprint_data.name}_Instance"
        
        with test_framework.test_connection() as conn:
            # Create and compile the blueprint first
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            test_framework.assert_response_success(create_response, "Failed to create blueprint")
            
            # Add a basic component
            comp_response = conn.send_command("add_component_to_blueprint", {
                "blueprint_name": blueprint_data.name,
                "component_type": "StaticMeshComponent", 
                "component_name": "StaticMesh"
            })
            test_framework.assert_response_success(comp_response, "Failed to add component")
            
            # Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile blueprint")
            
            # Spawn an actor from the blueprint
            spawn_response = conn.send_command("spawn_blueprint_actor", {
                "blueprint_name": blueprint_data.name,
                "actor_name": actor_name,
                "location": [0, 0, 100],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1]
            })
            test_framework.assert_response_success(spawn_response, "Failed to spawn blueprint actor")
            
            # Verify the actor exists in the level
            actors_response = conn.send_command("get_actors_in_level", {})
            test_framework.assert_response_success(actors_response, "Failed to get actors")
            
            actors = actors_response.get("result", [])
            actor_names = [actor.get("name") for actor in actors]
            assert actor_name in actor_names, f"Blueprint actor {actor_name} not found in level"
            
            # Clean up
            delete_actor_response = conn.send_command("delete_actor", {"name": actor_name})
            test_framework.assert_response_success(delete_actor_response, "Failed to delete blueprint actor")
            
            delete_blueprint_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_data.name
            })
    
    def test_set_static_mesh_properties(self, test_framework, clean_environment):
        """Test setting static mesh properties on a blueprint component."""
        blueprint_data = get_blueprint_data("simple_actor")
        
        with test_framework.test_connection() as conn:
            # Create the blueprint
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            test_framework.assert_response_success(create_response, "Failed to create blueprint")
            
            # Add static mesh component
            comp_response = conn.send_command("add_component_to_blueprint", {
                "blueprint_name": blueprint_data.name,
                "component_type": "StaticMeshComponent",
                "component_name": "StaticMesh"
            })
            test_framework.assert_response_success(comp_response, "Failed to add static mesh component")
            
            # Set static mesh properties
            mesh_props_response = conn.send_command("set_static_mesh_properties", {
                "blueprint_name": blueprint_data.name,
                "component_name": "StaticMesh",
                "static_mesh": "/Engine/BasicShapes/Cube"
            })
            test_framework.assert_response_success(mesh_props_response, "Failed to set static mesh properties")
            
            # Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile blueprint")
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_data.name
            })
    
    def test_set_physics_properties(self, test_framework, clean_environment):
        """Test setting physics properties on a blueprint component."""
        blueprint_data = get_blueprint_data("simple_actor")
        
        with test_framework.test_connection() as conn:
            # Create the blueprint
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            test_framework.assert_response_success(create_response, "Failed to create blueprint")
            
            # Add static mesh component
            comp_response = conn.send_command("add_component_to_blueprint", {
                "blueprint_name": blueprint_data.name,
                "component_type": "StaticMeshComponent",
                "component_name": "StaticMesh"
            })
            test_framework.assert_response_success(comp_response, "Failed to add component")
            
            # Set physics properties
            physics_response = conn.send_command("set_physics_properties", {
                "blueprint_name": blueprint_data.name,
                "component_name": "StaticMesh",
                "enable_physics": True,
                "physics_type": "Simulating"
            })
            test_framework.assert_response_success(physics_response, "Failed to set physics properties")
            
            # Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile blueprint")
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_data.name
            })
    
    def test_error_handling_invalid_parent_class(self, test_framework, clean_environment):
        """Test error handling for invalid parent class."""
        with test_framework.test_connection() as conn:
            response = conn.send_command("create_blueprint", {
                "name": "InvalidParentBP",
                "parent_class": "NonExistentClass",
                "path": "/Game/TestBP"
            })
            
            # This should result in an error
            test_framework.assert_response_error(response)
    
    def test_error_handling_invalid_component_type(self, test_framework, clean_environment):
        """Test error handling for invalid component type."""
        blueprint_name = "ErrorTestBP"
        
        with test_framework.test_connection() as conn:
            # Create a valid blueprint first
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_name,
                "parent_class": "Actor",
                "path": "/Game/TestBP"
            })
            test_framework.assert_response_success(create_response, "Failed to create test blueprint")
            
            # Try to add invalid component
            comp_response = conn.send_command("add_component_to_blueprint", {
                "blueprint_name": blueprint_name,
                "component_type": "NonExistentComponent",
                "component_name": "InvalidComp"
            })
            
            # This should result in an error
            test_framework.assert_response_error(comp_response)
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_name
            })
    
    @pytest.mark.slow
    def test_complex_blueprint_workflow(self, test_framework, clean_environment):
        """Test a complete complex blueprint creation workflow."""
        blueprint_data = get_blueprint_data("pawn_with_input")
        
        with test_framework.test_connection() as conn:
            start_time = time.time()
            
            # Step 1: Create the blueprint
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            test_framework.assert_response_success(create_response, "Failed to create blueprint")
            
            # Step 2: Add all components
            for component in blueprint_data.components:
                comp_response = conn.send_command("add_component_to_blueprint", {
                    "blueprint_name": blueprint_data.name,
                    "component_type": component.type,
                    "component_name": component.name
                })
                test_framework.assert_response_success(comp_response, f"Failed to add {component.name}")
            
            # Step 3: Add all variables
            for variable in blueprint_data.variables:
                var_response = conn.send_command("add_blueprint_variable", {
                    "blueprint_name": blueprint_data.name,
                    "variable_name": variable["name"],
                    "variable_type": variable["type"],
                    "default_value": variable.get("default_value")
                })
                test_framework.assert_response_success(var_response, f"Failed to add variable {variable['name']}")
            
            # Step 4: Set component properties
            mesh_response = conn.send_command("set_static_mesh_properties", {
                "blueprint_name": blueprint_data.name,
                "component_name": "Mesh",
                "static_mesh": "/Engine/BasicShapes/Sphere"
            })
            test_framework.assert_response_success(mesh_response, "Failed to set mesh properties")
            
            # Step 5: Set pawn properties
            pawn_response = conn.send_command("set_pawn_properties", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(pawn_response, "Failed to set pawn properties")
            
            # Step 6: Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_data.name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile blueprint")
            
            # Step 7: Spawn an instance
            actor_name = f"{blueprint_data.name}_Instance"
            spawn_response = conn.send_command("spawn_blueprint_actor", {
                "blueprint_name": blueprint_data.name,
                "actor_name": actor_name,
                "location": [0, 0, 100]
            })
            test_framework.assert_response_success(spawn_response, "Failed to spawn blueprint instance")
            
            workflow_duration = time.time() - start_time
            
            # Performance check - complex workflow should complete in reasonable time
            assert workflow_duration < 60.0, f"Complex blueprint workflow took too long: {workflow_duration:.2f}s"
            
            # Clean up
            delete_actor_response = conn.send_command("delete_actor", {"name": actor_name})
            delete_blueprint_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_data.name
            })
    
    def test_blueprint_compilation_status(self, test_framework, clean_environment):
        """Test checking blueprint compilation status."""
        blueprint_name = "CompilationTestBP"
        
        with test_framework.test_connection() as conn:
            # Create a simple blueprint
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_name,
                "parent_class": "Actor",
                "path": "/Game/TestBP"
            })
            test_framework.assert_response_success(create_response, "Failed to create blueprint")
            
            # Add a component to make it more realistic
            comp_response = conn.send_command("add_component_to_blueprint", {
                "blueprint_name": blueprint_name,
                "component_type": "StaticMeshComponent",
                "component_name": "TestMesh"
            })
            test_framework.assert_response_success(comp_response, "Failed to add component")
            
            # Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile blueprint")
            
            # Check compilation status (if command exists)
            status_response = conn.send_command("get_blueprint_status", {
                "blueprint_name": blueprint_name
            })
            
            # If the status command exists, verify the blueprint is compiled
            if status_response and status_response.get("success") is not False:
                status = status_response.get("result", {})
                # Verify compilation status if available
                if "is_compiled" in status:
                    assert status["is_compiled"], "Blueprint should be compiled"
                if "has_compile_errors" in status:
                    assert not status["has_compile_errors"], "Blueprint should not have compile errors"
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_name
            })

@pytest.mark.integration  
@pytest.mark.blueprints
@pytest.mark.requires_unreal
class TestBlueprintProperties:
    """Test blueprint property management."""
    
    def test_set_blueprint_property(self, test_framework, clean_environment):
        """Test setting blueprint-level properties."""
        blueprint_name = "PropertyTestBP"
        
        with test_framework.test_connection() as conn:
            # Create the blueprint
            create_response = conn.send_command("create_blueprint", {
                "name": blueprint_name,
                "parent_class": "Actor",
                "path": "/Game/TestBP"
            })
            test_framework.assert_response_success(create_response, "Failed to create blueprint")
            
            # Set blueprint properties
            prop_response = conn.send_command("set_blueprint_property", {
                "blueprint_name": blueprint_name,
                "property_name": "ReplicateMovement", 
                "property_value": True
            })
            test_framework.assert_response_success(prop_response, "Failed to set blueprint property")
            
            # Compile the blueprint
            compile_response = conn.send_command("compile_blueprint", {
                "blueprint_name": blueprint_name
            })
            test_framework.assert_response_success(compile_response, "Failed to compile blueprint")
            
            # Clean up
            delete_response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_name
            })