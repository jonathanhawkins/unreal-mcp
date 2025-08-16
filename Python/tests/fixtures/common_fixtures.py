"""
Common test fixtures for Unreal MCP tests.

Provides reusable fixtures for setting up and tearing down test environments,
creating test actors, managing test data, and handling cleanup operations.
"""

import pytest
import time
from typing import List, Dict, Any, Generator
from contextlib import contextmanager

from ..test_framework import TestFramework, TestConfig
from ..data.test_data import get_test_data_manager, ActorTestData, BlueprintTestData

class TestActorManager:
    """Manage test actors with automatic cleanup."""
    
    def __init__(self, framework: TestFramework):
        self.framework = framework
        self.created_actors = []
        self.spawned_blueprints = []
        
    def spawn_test_actor(self, actor_data: ActorTestData) -> Dict[str, Any]:
        """Spawn a test actor and track it for cleanup."""
        with self.framework.test_connection() as conn:
            response = conn.send_command("spawn_actor", {
                "name": actor_data.name,
                "type": actor_data.type,
                "location": actor_data.location,
                "rotation": actor_data.rotation,
                "scale": actor_data.scale
            })
            
            if response and response.get("success") is not False and response.get("status") != "error":
                self.created_actors.append(actor_data.name)
                
            return response
            
    def spawn_test_blueprint(self, blueprint_name: str, actor_name: str) -> Dict[str, Any]:
        """Spawn a blueprint actor and track it for cleanup.""" 
        with self.framework.test_connection() as conn:
            response = conn.send_command("spawn_blueprint_actor", {
                "blueprint_name": blueprint_name,
                "actor_name": actor_name
            })
            
            if response and response.get("success") is not False and response.get("status") != "error":
                self.spawned_blueprints.append(actor_name)
                
            return response
            
    def delete_actor(self, actor_name: str) -> Dict[str, Any]:
        """Delete a specific actor."""
        with self.framework.test_connection() as conn:
            response = conn.send_command("delete_actor", {"name": actor_name})
            
            # Remove from tracking lists
            if actor_name in self.created_actors:
                self.created_actors.remove(actor_name)
            if actor_name in self.spawned_blueprints:
                self.spawned_blueprints.remove(actor_name)
                
            return response
            
    def cleanup_all_actors(self):
        """Clean up all tracked actors."""
        all_actors = self.created_actors + self.spawned_blueprints
        
        for actor_name in all_actors:
            try:
                self.delete_actor(actor_name)
            except Exception as e:
                print(f"Warning: Failed to cleanup actor {actor_name}: {e}")
                
        self.created_actors.clear()
        self.spawned_blueprints.clear()

class TestBlueprintManager:
    """Manage test blueprints with automatic cleanup."""
    
    def __init__(self, framework: TestFramework):
        self.framework = framework
        self.created_blueprints = []
        
    def create_test_blueprint(self, blueprint_data: BlueprintTestData) -> Dict[str, Any]:
        """Create a test blueprint and track it for cleanup."""
        with self.framework.test_connection() as conn:
            # Create the blueprint
            response = conn.send_command("create_blueprint", {
                "name": blueprint_data.name,
                "parent_class": blueprint_data.parent_class,
                "path": blueprint_data.path
            })
            
            if response and response.get("success") is not False and response.get("status") != "error":
                self.created_blueprints.append(blueprint_data.name)
                
                # Add components
                for component in blueprint_data.components:
                    comp_response = conn.send_command("add_component_to_blueprint", {
                        "blueprint_name": blueprint_data.name,
                        "component_type": component.type,
                        "component_name": component.name
                    })
                    
                    # Set component properties
                    for prop_name, prop_value in component.properties.items():
                        prop_response = conn.send_command("set_component_property", {
                            "blueprint_name": blueprint_data.name,
                            "component_name": component.name,
                            "property_name": prop_name,
                            "property_value": prop_value
                        })
                
                # Add variables
                for variable in blueprint_data.variables:
                    var_response = conn.send_command("add_blueprint_variable", {
                        "blueprint_name": blueprint_data.name,
                        "variable_name": variable["name"],
                        "variable_type": variable["type"],
                        "default_value": variable.get("default_value")
                    })
                
                # Compile the blueprint
                compile_response = conn.send_command("compile_blueprint", {
                    "blueprint_name": blueprint_data.name
                })
                
            return response
            
    def delete_blueprint(self, blueprint_name: str) -> Dict[str, Any]:
        """Delete a specific blueprint."""
        with self.framework.test_connection() as conn:
            response = conn.send_command("delete_blueprint", {
                "blueprint_name": blueprint_name
            })
            
            if blueprint_name in self.created_blueprints:
                self.created_blueprints.remove(blueprint_name)
                
            return response
            
    def cleanup_all_blueprints(self):
        """Clean up all tracked blueprints.""" 
        for blueprint_name in self.created_blueprints:
            try:
                self.delete_blueprint(blueprint_name)
            except Exception as e:
                print(f"Warning: Failed to cleanup blueprint {blueprint_name}: {e}")
                
        self.created_blueprints.clear()

class TestEnvironmentManager:
    """Manage test environment setup and teardown."""
    
    def __init__(self, framework: TestFramework):
        self.framework = framework
        self.actor_manager = TestActorManager(framework)
        self.blueprint_manager = TestBlueprintManager(framework)
        self.original_actors = []
        
    def setup_clean_environment(self):
        """Set up a clean test environment."""
        # Get initial actors for restoration
        with self.framework.test_connection() as conn:
            response = conn.send_command("get_actors_in_level", {})
            if response and response.get("result"):
                self.original_actors = [actor.get("name") for actor in response["result"]]
                
    def cleanup_environment(self):
        """Clean up the test environment."""
        # Clean up managed resources
        self.actor_manager.cleanup_all_actors()
        self.blueprint_manager.cleanup_all_blueprints()
        
        # Remove any extra actors that weren't part of the original level
        with self.framework.test_connection() as conn:
            response = conn.send_command("get_actors_in_level", {})
            if response and response.get("result"):
                current_actors = [actor.get("name") for actor in response["result"]]
                
                for actor_name in current_actors:
                    if actor_name not in self.original_actors:
                        try:
                            conn.send_command("delete_actor", {"name": actor_name})
                        except Exception as e:
                            print(f"Warning: Failed to cleanup extra actor {actor_name}: {e}")

@pytest.fixture
def test_data():
    """Provide test data manager."""
    return get_test_data_manager()

@pytest.fixture 
def actor_manager(test_framework):
    """Provide actor manager with automatic cleanup."""
    manager = TestActorManager(test_framework)
    yield manager
    manager.cleanup_all_actors()

@pytest.fixture
def blueprint_manager(test_framework):
    """Provide blueprint manager with automatic cleanup."""
    manager = TestBlueprintManager(test_framework)
    yield manager
    manager.cleanup_all_blueprints()

@pytest.fixture
def clean_environment(test_framework):
    """Provide a clean test environment with automatic cleanup."""
    manager = TestEnvironmentManager(test_framework)
    manager.setup_clean_environment()
    yield manager
    manager.cleanup_environment()

@pytest.fixture
def unreal_connection_test(test_framework):
    """Test Unreal connection and skip if not available."""
    if not test_framework.test_unreal_connection():
        pytest.skip("Unreal Engine connection not available")
    return True

@contextmanager
def temporary_actors(framework: TestFramework, actor_data_list: List[ActorTestData]):
    """Context manager for temporary actors that are automatically cleaned up."""
    manager = TestActorManager(framework)
    created_actors = []
    
    try:
        for actor_data in actor_data_list:
            response = manager.spawn_test_actor(actor_data)
            if response and response.get("success") is not False:
                created_actors.append(actor_data.name)
        yield created_actors
    finally:
        manager.cleanup_all_actors()

@contextmanager
def temporary_blueprints(framework: TestFramework, blueprint_data_list: List[BlueprintTestData]):
    """Context manager for temporary blueprints that are automatically cleaned up."""
    manager = TestBlueprintManager(framework)
    created_blueprints = []
    
    try:
        for blueprint_data in blueprint_data_list:
            response = manager.create_test_blueprint(blueprint_data)
            if response and response.get("success") is not False:
                created_blueprints.append(blueprint_data.name)
        yield created_blueprints
    finally:
        manager.cleanup_all_blueprints()

def wait_for_compilation(framework: TestFramework, blueprint_name: str, timeout: float = 10.0) -> bool:
    """Wait for blueprint compilation to complete."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        with framework.test_connection() as conn:
            response = conn.send_command("get_blueprint_status", {
                "blueprint_name": blueprint_name
            })
            
            if response and response.get("result", {}).get("is_compiled"):
                return True
                
        time.sleep(0.5)
        
    return False

def assert_actors_exist(framework: TestFramework, actor_names: List[str]):
    """Assert that specific actors exist in the level."""
    with framework.test_connection() as conn:
        response = conn.send_command("get_actors_in_level", {})
        framework.assert_response_success(response, "Failed to get actors in level")
        
        existing_actors = response.get("result", [])
        existing_names = [actor.get("name") for actor in existing_actors]
        
        for actor_name in actor_names:
            assert actor_name in existing_names, f"Actor '{actor_name}' not found in level"

def assert_actors_not_exist(framework: TestFramework, actor_names: List[str]):
    """Assert that specific actors do not exist in the level."""
    with framework.test_connection() as conn:
        response = conn.send_command("get_actors_in_level", {})
        framework.assert_response_success(response, "Failed to get actors in level")
        
        existing_actors = response.get("result", [])
        existing_names = [actor.get("name") for actor in existing_actors]
        
        for actor_name in actor_names:
            assert actor_name not in existing_names, f"Actor '{actor_name}' should not exist in level"

def assert_blueprint_compiled(framework: TestFramework, blueprint_name: str):
    """Assert that a blueprint is successfully compiled."""
    with framework.test_connection() as conn:
        response = conn.send_command("get_blueprint_status", {
            "blueprint_name": blueprint_name
        })
        framework.assert_response_success(response, f"Failed to get status for blueprint {blueprint_name}")
        
        status = response.get("result", {})
        assert status.get("is_compiled", False), f"Blueprint {blueprint_name} is not compiled"
        assert not status.get("has_compile_errors", True), f"Blueprint {blueprint_name} has compile errors"

def measure_operation_time(operation_func, *args, **kwargs) -> tuple:
    """Measure the execution time of an operation."""
    start_time = time.time()
    result = operation_func(*args, **kwargs)
    end_time = time.time()
    duration = end_time - start_time
    return result, duration

def retry_operation(operation_func, max_retries: int = 3, delay: float = 1.0, *args, **kwargs):
    """Retry an operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))
    
    return None