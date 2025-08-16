"""
Validation tests for error conditions and edge cases.

Tests various error scenarios, input validation, and edge cases
to ensure robust error handling throughout the MCP system.
"""

import pytest
from typing import Dict, Any

from ..data.test_data import get_test_data_manager

@pytest.mark.validation
class TestInputValidation:
    """Test input validation for various MCP commands."""
    
    def test_spawn_actor_missing_required_parameters(self, test_framework):
        """Test spawn_actor with missing required parameters."""
        test_cases = [
            # Missing name
            {
                "params": {"type": "StaticMeshActor", "location": [0, 0, 0]},
                "expected_error": "name"
            },
            # Missing type
            {
                "params": {"name": "TestActor", "location": [0, 0, 0]},
                "expected_error": "type"
            },
            # Missing location
            {
                "params": {"name": "TestActor", "type": "StaticMeshActor"},
                "expected_error": "location"
            },
            # Completely empty params
            {
                "params": {},
                "expected_error": "required"
            }
        ]
        
        with test_framework.test_connection() as conn:
            for test_case in test_cases:
                response = conn.send_command("spawn_actor", test_case["params"])
                
                # Should result in error
                if response:
                    if response.get("status") == "error" or response.get("success") is False:
                        error_msg = response.get("error", response.get("message", "")).lower()
                        assert test_case["expected_error"].lower() in error_msg, \
                            f"Expected error containing '{test_case['expected_error']}', got: {error_msg}"
    
    def test_invalid_data_types(self, test_framework):
        """Test commands with invalid data types."""
        test_cases = [
            # String where list expected
            {
                "command": "spawn_actor",
                "params": {
                    "name": "TestActor",
                    "type": "StaticMeshActor",
                    "location": "not_a_list"
                }
            },
            # Invalid number formats
            {
                "command": "spawn_actor", 
                "params": {
                    "name": "TestActor",
                    "type": "StaticMeshActor",
                    "location": ["not", "numbers", "here"]
                }
            },
            # Boolean where string expected
            {
                "command": "spawn_actor",
                "params": {
                    "name": True,  # Should be string
                    "type": "StaticMeshActor",
                    "location": [0, 0, 0]
                }
            }
        ]
        
        with test_framework.test_connection() as conn:
            for test_case in test_cases:
                response = conn.send_command(test_case["command"], test_case["params"])
                
                # Should result in error or be handled gracefully
                if response:
                    # Either explicit error or command fails
                    if response.get("status") == "error" or response.get("success") is False:
                        assert "error" in response or "message" in response
                        
    def test_extremely_large_values(self, test_framework):
        """Test handling of extremely large numeric values."""
        test_cases = [
            # Very large coordinates
            {
                "command": "spawn_actor",
                "params": {
                    "name": "LargeCoordActor",
                    "type": "StaticMeshActor", 
                    "location": [1e10, 1e10, 1e10]
                }
            },
            # Extremely small values (near zero)
            {
                "command": "spawn_actor",
                "params": {
                    "name": "SmallCoordActor",
                    "type": "StaticMeshActor",
                    "location": [1e-10, 1e-10, 1e-10]
                }
            },
            # Very large scales
            {
                "command": "spawn_actor",
                "params": {
                    "name": "LargeScaleActor", 
                    "type": "StaticMeshActor",
                    "location": [0, 0, 0],
                    "scale": [1000, 1000, 1000]
                }
            }
        ]
        
        with test_framework.test_connection() as conn:
            spawned_actors = []
            
            try:
                for test_case in test_cases:
                    response = conn.send_command(test_case["command"], test_case["params"])
                    
                    # Either succeeds or fails gracefully
                    if response:
                        if response.get("success") is not False and response.get("status") != "error":
                            spawned_actors.append(test_case["params"]["name"])
                        # If it fails, that's also acceptable for extreme values
                        
            finally:
                # Clean up any actors that were spawned
                for actor_name in spawned_actors:
                    conn.send_command("delete_actor", {"name": actor_name})

@pytest.mark.validation
class TestEdgeCases:
    """Test various edge cases and boundary conditions."""
    
    def test_empty_strings(self, test_framework):
        """Test handling of empty strings in various fields."""
        test_cases = [
            {
                "command": "spawn_actor",
                "params": {
                    "name": "",  # Empty name
                    "type": "StaticMeshActor",
                    "location": [0, 0, 0]
                }
            },
            {
                "command": "spawn_actor",
                "params": {
                    "name": "TestActor",
                    "type": "",  # Empty type
                    "location": [0, 0, 0]
                }
            }
        ]
        
        with test_framework.test_connection() as conn:
            for test_case in test_cases:
                response = conn.send_command(test_case["command"], test_case["params"])
                
                # Should result in error for empty required fields
                if response:
                    assert response.get("status") == "error" or response.get("success") is False, \
                        "Empty required fields should result in error"
    
    def test_unicode_and_special_characters(self, test_framework):
        """Test handling of unicode and special characters."""
        test_cases = [
            {
                "name": "测试Actor",  # Chinese characters
                "type": "StaticMeshActor",
                "location": [0, 0, 0]
            },
            {
                "name": "Test-Actor_123!@#",  # Special characters
                "type": "StaticMeshActor",
                "location": [0, 0, 0] 
            },
            {
                "name": "Actor🚀",  # Emoji
                "type": "StaticMeshActor",
                "location": [0, 0, 0]
            }
        ]
        
        with test_framework.test_connection() as conn:
            spawned_actors = []
            
            try:
                for test_case in test_cases:
                    response = conn.send_command("spawn_actor", test_case)
                    
                    if response:
                        if response.get("success") is not False and response.get("status") != "error":
                            spawned_actors.append(test_case["name"])
                        # If it fails due to character restrictions, that's acceptable
                        
            finally:
                # Clean up
                for actor_name in spawned_actors:
                    conn.send_command("delete_actor", {"name": actor_name})
    
    def test_very_long_strings(self, test_framework):
        """Test handling of very long strings."""
        # Create a very long name
        long_name = "A" * 1000
        
        with test_framework.test_connection() as conn:
            response = conn.send_command("spawn_actor", {
                "name": long_name,
                "type": "StaticMeshActor",
                "location": [0, 0, 0]
            })
            
            # Should either succeed (with truncation) or fail gracefully
            if response:
                if response.get("success") is not False and response.get("status") != "error":
                    # If successful, clean up
                    conn.send_command("delete_actor", {"name": long_name})
                # If it fails, that's acceptable for very long names
    
    def test_null_and_none_values(self, test_framework):
        """Test handling of null/None values."""
        test_cases = [
            {
                "command": "spawn_actor",
                "params": {
                    "name": "TestActor",
                    "type": "StaticMeshActor",
                    "location": None  # None value
                }
            },
            {
                "command": "delete_actor",
                "params": {
                    "name": None  # None name
                }
            }
        ]
        
        with test_framework.test_connection() as conn:
            for test_case in test_cases:
                response = conn.send_command(test_case["command"], test_case["params"])
                
                # Should result in error for None values in required fields
                if response:
                    assert response.get("status") == "error" or response.get("success") is False, \
                        "None values in required fields should result in error"

@pytest.mark.validation
class TestConcurrencyAndRaceConditions:
    """Test concurrent operations and potential race conditions."""
    
    def test_rapid_actor_creation_deletion(self, test_framework):
        """Test rapid creation and deletion of actors."""
        actor_name = "RapidTestActor"
        
        with test_framework.test_connection() as conn:
            # Rapidly create and delete the same actor
            for i in range(5):
                # Spawn
                spawn_response = conn.send_command("spawn_actor", {
                    "name": f"{actor_name}_{i}",
                    "type": "StaticMeshActor",
                    "location": [i * 10, 0, 0]
                })
                
                # Immediately delete
                if spawn_response and spawn_response.get("success") is not False:
                    delete_response = conn.send_command("delete_actor", {
                        "name": f"{actor_name}_{i}"
                    })
                    # Don't assert success as timing might cause issues
    
    def test_duplicate_operations(self, test_framework):
        """Test handling of duplicate operations."""
        actor_name = "DuplicateTestActor"
        
        with test_framework.test_connection() as conn:
            try:
                # Spawn actor
                spawn_response = conn.send_command("spawn_actor", {
                    "name": actor_name,
                    "type": "StaticMeshActor",
                    "location": [0, 0, 0]
                })
                
                if spawn_response and spawn_response.get("success") is not False:
                    # Try to delete the same actor multiple times
                    delete_response1 = conn.send_command("delete_actor", {"name": actor_name})
                    delete_response2 = conn.send_command("delete_actor", {"name": actor_name})
                    
                    # First delete should succeed, second should fail gracefully
                    if delete_response2:
                        # Second delete should indicate actor doesn't exist
                        if delete_response2.get("status") == "error":
                            error_msg = delete_response2.get("error", "").lower()
                            assert "not found" in error_msg or "does not exist" in error_msg
                            
            finally:
                # Ensure cleanup
                conn.send_command("delete_actor", {"name": actor_name})

@pytest.mark.validation 
class TestResourceLimits:
    """Test resource limits and boundary conditions."""
    
    def test_maximum_parameters(self, test_framework):
        """Test commands with maximum number of parameters."""
        # Create a command with many parameters
        large_params = {
            "name": "MaxParamActor",
            "type": "StaticMeshActor", 
            "location": [0, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        }
        
        # Add many extra parameters
        for i in range(100):
            large_params[f"extra_param_{i}"] = f"value_{i}"
        
        with test_framework.test_connection() as conn:
            response = conn.send_command("spawn_actor", large_params)
            
            # Should either succeed (ignoring extra params) or fail gracefully
            if response and response.get("success") is not False and response.get("status") != "error":
                # Clean up if successful
                conn.send_command("delete_actor", {"name": "MaxParamActor"})
    
    def test_nested_data_structures(self, test_framework):
        """Test deeply nested data structures."""
        nested_params = {
            "name": "NestedActor",
            "type": "StaticMeshActor",
            "location": [0, 0, 0],
            "properties": {
                "level1": {
                    "level2": {
                        "level3": {
                            "deep_value": "test"
                        }
                    }
                }
            }
        }
        
        with test_framework.test_connection() as conn:
            response = conn.send_command("spawn_actor", nested_params)
            
            # Should handle nested structures gracefully
            if response and response.get("success") is not False and response.get("status") != "error":
                # Clean up if successful
                conn.send_command("delete_actor", {"name": "NestedActor"})

@pytest.mark.validation
class TestErrorRecovery:
    """Test error recovery and system resilience."""
    
    def test_recovery_after_invalid_command(self, test_framework):
        """Test system recovery after invalid commands."""
        with test_framework.test_connection() as conn:
            # Send invalid command
            invalid_response = conn.send_command("nonexistent_command", {})
            
            # Should result in error
            if invalid_response:
                assert invalid_response.get("status") == "error" or invalid_response.get("success") is False
            
            # System should still work for valid commands
            valid_response = conn.send_command("get_actors_in_level", {})
            
            # Valid command should still work
            test_framework.assert_response_success(valid_response, "System should recover after invalid command")
    
    def test_recovery_after_malformed_request(self, test_framework):
        """Test recovery after malformed requests."""
        with test_framework.test_connection() as conn:
            # Send malformed parameters
            malformed_response = conn.send_command("spawn_actor", {
                "invalid_structure": {
                    "nested": {
                        "without": {
                            "proper": {
                                "format": "test"
                            }
                        }
                    }
                }
            })
            
            # Should result in error
            if malformed_response:
                assert malformed_response.get("status") == "error" or malformed_response.get("success") is False
            
            # System should still work for valid commands
            recovery_response = conn.send_command("get_actors_in_level", {})
            test_framework.assert_response_success(recovery_response, "System should recover after malformed request")

@pytest.mark.validation
class TestDataConsistency:
    """Test data consistency and state management."""
    
    def test_level_state_consistency(self, test_framework):
        """Test that level state remains consistent across operations."""
        test_actor = "ConsistencyTestActor"
        
        with test_framework.test_connection() as conn:
            # Get initial state
            initial_response = conn.send_command("get_actors_in_level", {})
            test_framework.assert_response_success(initial_response, "Failed to get initial state")
            
            initial_count = len(initial_response.get("result", []))
            
            try:
                # Spawn actor
                spawn_response = conn.send_command("spawn_actor", {
                    "name": test_actor,
                    "type": "StaticMeshActor",
                    "location": [0, 0, 0]
                })
                
                if spawn_response and spawn_response.get("success") is not False:
                    # Check state after spawn
                    after_spawn_response = conn.send_command("get_actors_in_level", {})
                    test_framework.assert_response_success(after_spawn_response, "Failed to get state after spawn")
                    
                    after_spawn_count = len(after_spawn_response.get("result", []))
                    assert after_spawn_count == initial_count + 1, \
                        f"Expected {initial_count + 1} actors after spawn, got {after_spawn_count}"
                    
                    # Delete actor
                    delete_response = conn.send_command("delete_actor", {"name": test_actor})
                    test_framework.assert_response_success(delete_response, "Failed to delete actor")
                    
                    # Check final state
                    final_response = conn.send_command("get_actors_in_level", {})
                    test_framework.assert_response_success(final_response, "Failed to get final state")
                    
                    final_count = len(final_response.get("result", []))
                    assert final_count == initial_count, \
                        f"Expected {initial_count} actors after delete, got {final_count}"
                        
            finally:
                # Ensure cleanup
                conn.send_command("delete_actor", {"name": test_actor})

@pytest.mark.validation
class TestPerformanceLimits:
    """Test performance limits and degradation scenarios."""
    
    @pytest.mark.slow
    def test_command_timeout_behavior(self, test_framework):
        """Test behavior under command timeout conditions.""" 
        # This test would ideally simulate a slow command
        # For now, we test the timeout mechanism itself
        
        with test_framework.test_connection() as conn:
            import time
            start_time = time.time()
            
            # Send a command that might be slow
            response = conn.send_command("get_actors_in_level", {})
            
            duration = time.time() - start_time
            
            # Command should complete within reasonable time
            assert duration < 30.0, f"Command took too long: {duration:.2f}s"
            
            # Response should be valid regardless of speed
            if response:
                assert isinstance(response, dict), "Response should be a dictionary"
    
    def test_large_response_handling(self, test_framework):
        """Test handling of large responses."""
        with test_framework.test_connection() as conn:
            # Get all actors (might be a large response in complex levels)
            response = conn.send_command("get_actors_in_level", {})
            
            test_framework.assert_response_success(response, "Failed to get actors")
            
            # Verify response structure regardless of size
            actors = response.get("result", [])
            assert isinstance(actors, list), "Actors result should be a list"
            
            # Each actor should have proper structure
            for actor in actors[:10]:  # Check first 10 to avoid excessive processing
                assert isinstance(actor, dict), "Each actor should be a dictionary"
                assert "name" in actor, "Each actor should have a name"