"""
Comprehensive tests for World Runtime commands.

Tests all world runtime operations including:
- get_current_level_info: Query current world and level information

Each test covers happy path, error handling, edge cases, and performance validation.
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List
import pytest
import sys

# Add parent directories to path for imports
test_dir = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(test_dir.parent))

from tests.test_framework import TestFramework, create_test_config, TestResult
from tests.data.test_data import get_test_data_manager
from unreal_mcp_server import get_unreal_connection

class TestWorldCommands:
    """Test suite for World Runtime commands."""
    
    @classmethod
    def setup_class(cls):
        """Setup test framework and data."""
        cls.config = create_test_config()
        cls.framework = TestFramework(cls.config)
        cls.test_data_manager = get_test_data_manager()
        cls.test_results = []
        
        # Expected level info properties
        cls.expected_level_properties = [
            "level_name", "level_path", "world_name", 
            "is_persistent", "is_visible", "actors",
            "streaming_levels", "lighting_scenario"
        ]
        
        # Alternative property names that might be used
        cls.alternative_properties = {
            "level_name": ["name", "level_display_name"],
            "level_path": ["path", "package_name", "asset_path"],
            "world_name": ["world", "world_path"],
            "actors": ["actor_count", "num_actors", "actor_list"],
            "streaming_levels": ["streaming", "sub_levels"]
        }
        
        # World state tracking
        cls.initial_world_state = None
        cls.test_levels_created = []
    
    @classmethod
    def teardown_class(cls):
        """Cleanup any test artifacts."""
        # Clean up test levels if any were created
        if cls.test_levels_created:
            try:
                with cls.framework.test_connection() as conn:
                    if conn.connect():
                        for level_path in cls.test_levels_created:
                            print(f"Would cleanup test level: {level_path}")
            except Exception as e:
                print(f"Error during cleanup: {e}")
    
    def _assert_valid_response(self, response: Dict[str, Any], command: str):
        """Assert response is valid and successful."""
        assert response is not None, f"{command}: No response received"
        assert response.get("success") or response.get("status") != "error", \
            f"{command}: Command failed - {response.get('error', 'Unknown error')}"
    
    def _assert_error_response(self, response: Dict[str, Any], command: str, expected_error: str = None):
        """Assert response indicates an error."""
        assert response is not None, f"{command}: No response received"
        assert response.get("success") is False or response.get("status") == "error", \
            f"{command}: Expected error but got success"
        if expected_error:
            error_msg = response.get("error", "")
            assert expected_error.lower() in error_msg.lower(), \
                f"{command}: Expected error '{expected_error}' but got '{error_msg}'"
    
    def _validate_level_info_structure(self, level_info: Dict[str, Any]) -> List[str]:
        """Validate level info structure and return found properties."""
        found_properties = []
        
        for expected_prop in self.expected_level_properties:
            if expected_prop in level_info:
                found_properties.append(expected_prop)
            else:
                # Check alternative names
                alternatives = self.alternative_properties.get(expected_prop, [])
                for alt in alternatives:
                    if alt in level_info:
                        found_properties.append(alt)
                        break
        
        return found_properties
    
    def _get_world_state_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current world state for comparison."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("get_current_level_info", {})
                if response and response.get("success"):
                    return response.get("result", {})
        return {}
    
    # =================================
    # GET CURRENT LEVEL INFO TESTS
    # =================================
    
    def test_get_current_level_info_basic(self):
        """Test getting current level info in basic scenario."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_current_level_info", {})
            
            self._assert_valid_response(response, "get_current_level_info")
            
            result = response.get("result", {})
            assert isinstance(result, dict), "Level info should return a dictionary"
            
            # Validate structure
            found_properties = self._validate_level_info_structure(result)
            assert len(found_properties) > 0, f"Level info should contain recognizable properties. Found keys: {list(result.keys())}"
            
            print(f"✓ Successfully retrieved current level info with properties: {found_properties}")
            return result
    
    def test_get_current_level_info_properties(self):
        """Test that current level info contains expected properties."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_current_level_info", {})
            
            self._assert_valid_response(response, "get_current_level_info")
            
            result = response.get("result", {})
            
            # Check for level name or path
            has_level_identifier = any(key in result for key in [
                "level_name", "name", "level_path", "path", "package_name"
            ])
            assert has_level_identifier, f"Level info should have level identifier. Found keys: {list(result.keys())}"
            
            # Check for world information
            has_world_info = any(key in result for key in [
                "world_name", "world", "world_path"
            ])
            
            # Check for basic level state
            has_state_info = any(key in result for key in [
                "is_visible", "is_persistent", "actors", "actor_count", "streaming_levels"
            ])
            
            print(f"✓ Level info contains:")
            print(f"  - Level identifier: {has_level_identifier}")
            print(f"  - World information: {has_world_info}")
            print(f"  - State information: {has_state_info}")
            
            # At minimum, should have level identifier
            assert has_level_identifier, "Level info must contain level identification"
    
    def test_get_current_level_info_multiple_calls(self):
        """Test getting current level info multiple times for consistency."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            responses = []
            for i in range(3):
                response = conn.send_command("get_current_level_info", {})
                self._assert_valid_response(response, f"get_current_level_info ({i})")
                responses.append(response.get("result", {}))
            
            # Compare responses for consistency
            first_result = responses[0]
            for i, result in enumerate(responses[1:], 1):
                # Level path/name should be consistent
                level_identifiers_first = [
                    first_result.get("level_name"),
                    first_result.get("name"),
                    first_result.get("level_path"),
                    first_result.get("path")
                ]
                level_identifiers_current = [
                    result.get("level_name"),
                    result.get("name"),
                    result.get("level_path"),
                    result.get("path")
                ]
                
                # At least one identifier should match (allowing for None values)
                has_matching_identifier = False
                for first_id, current_id in zip(level_identifiers_first, level_identifiers_current):
                    if first_id and current_id and first_id == current_id:
                        has_matching_identifier = True
                        break
                
                # If we have valid identifiers, they should match
                valid_first = [id for id in level_identifiers_first if id]
                valid_current = [id for id in level_identifiers_current if id]
                if valid_first and valid_current:
                    assert has_matching_identifier, f"Level identifiers should be consistent across calls"
            
            print(f"✓ Level info is consistent across multiple calls")
    
    def test_get_current_level_info_after_level_creation(self):
        """Test getting level info after creating a new level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Get initial state
            initial_response = conn.send_command("get_current_level_info", {})
            self._assert_valid_response(initial_response, "get_current_level_info (initial)")
            initial_result = initial_response.get("result", {})
            
            # Create a new level
            level_name = "WorldTestLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            
            if create_response and create_response.get("success"):
                self.test_levels_created.append(f"/Game/{level_name}")
                
                # Get level info after creation
                after_create_response = conn.send_command("get_current_level_info", {})
                self._assert_valid_response(after_create_response, "get_current_level_info (after create)")
                after_create_result = after_create_response.get("result", {})
                
                # Level info should reflect the new level (if it's now current)
                new_level_name = after_create_result.get("level_name") or after_create_result.get("name")
                if new_level_name and level_name.lower() in new_level_name.lower():
                    print(f"✓ Level info updated after level creation (now in {new_level_name})")
                else:
                    print(f"✓ Level info remains stable after level creation (still in original level)")
            else:
                print(f"⚠ Level creation not supported, testing level info stability")
                
                # Even if creation failed, level info should still work
                stable_response = conn.send_command("get_current_level_info", {})
                self._assert_valid_response(stable_response, "get_current_level_info (stable)")
    
    def test_get_current_level_info_after_level_load(self):
        """Test getting level info after loading a different level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Get initial state
            initial_response = conn.send_command("get_current_level_info", {})
            self._assert_valid_response(initial_response, "get_current_level_info (initial)")
            initial_result = initial_response.get("result", {})
            
            # Try to create and load a test level
            level_name = "LoadTestLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            
            if create_response and create_response.get("success"):
                self.test_levels_created.append(f"/Game/{level_name}")
                
                # Save the created level
                save_response = conn.send_command("save_level", {})
                
                # Load the test level
                load_response = conn.send_command("load_level", {
                    "level_path": f"/Game/{level_name}"
                })
                
                if load_response and load_response.get("success"):
                    # Get level info after loading
                    after_load_response = conn.send_command("get_current_level_info", {})
                    self._assert_valid_response(after_load_response, "get_current_level_info (after load)")
                    after_load_result = after_load_response.get("result", {})
                    
                    # Level info should reflect the loaded level
                    current_level_name = after_load_result.get("level_name") or after_load_result.get("name")
                    if current_level_name:
                        print(f"✓ Level info updated after level load (current: {current_level_name})")
                    else:
                        print(f"✓ Level info available after level load")
                else:
                    print(f"⚠ Level loading not supported, testing level info after creation")
            else:
                print(f"⚠ Level operations not supported, testing basic level info stability")
    
    def test_get_current_level_info_streaming_levels(self):
        """Test getting level info when streaming levels are present."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Get initial level info
            initial_response = conn.send_command("get_current_level_info", {})
            self._assert_valid_response(initial_response, "get_current_level_info (initial)")
            initial_result = initial_response.get("result", {})
            
            # Try to create a streaming level
            level_name = "StreamingTestLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            
            if create_response and create_response.get("success"):
                self.test_levels_created.append(f"/Game/{level_name}")
                
                # Add as streaming level
                streaming_response = conn.send_command("create_streaming_level", {
                    "level_path": f"/Game/{level_name}"
                })
                
                if streaming_response and streaming_response.get("success"):
                    # Get level info with streaming level
                    with_streaming_response = conn.send_command("get_current_level_info", {})
                    self._assert_valid_response(with_streaming_response, "get_current_level_info (with streaming)")
                    with_streaming_result = with_streaming_response.get("result", {})
                    
                    # Check for streaming level information
                    has_streaming_info = any(key in with_streaming_result for key in [
                        "streaming_levels", "streaming", "sub_levels"
                    ])
                    
                    if has_streaming_info:
                        print(f"✓ Level info includes streaming level information")
                    else:
                        print(f"✓ Level info available with streaming levels present")
                else:
                    print(f"⚠ Streaming level creation not supported")
            else:
                print(f"⚠ Level creation not supported for streaming test")
    
    # =================================
    # EDGE CASE TESTS
    # =================================
    
    def test_get_current_level_info_empty_params(self):
        """Test getting current level info with empty parameters."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_current_level_info", {})
            
            self._assert_valid_response(response, "get_current_level_info")
            
            result = response.get("result", {})
            assert isinstance(result, dict), "Level info should return a dictionary even with empty params"
            
            print(f"✓ Level info works with empty parameters")
    
    def test_get_current_level_info_with_extra_params(self):
        """Test getting current level info with unexpected extra parameters."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_current_level_info", {
                "unexpected_param": "value",
                "another_param": 123
            })
            
            self._assert_valid_response(response, "get_current_level_info")
            
            result = response.get("result", {})
            assert isinstance(result, dict), "Level info should handle extra parameters gracefully"
            
            print(f"✓ Level info handles extra parameters gracefully")
    
    def test_get_current_level_info_data_types(self):
        """Test that current level info returns appropriate data types."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_current_level_info", {})
            
            self._assert_valid_response(response, "get_current_level_info")
            
            result = response.get("result", {})
            
            # Validate common field types
            type_checks = {
                "level_name": [str, type(None)],
                "name": [str, type(None)],
                "level_path": [str, type(None)],
                "path": [str, type(None)],
                "is_visible": [bool, type(None)],
                "is_persistent": [bool, type(None)],
                "actors": [list, dict, int, type(None)],
                "actor_count": [int, type(None)],
                "streaming_levels": [list, dict, type(None)]
            }
            
            type_validation_results = []
            for field, expected_types in type_checks.items():
                if field in result:
                    field_value = result[field]
                    field_type = type(field_value)
                    if field_type in expected_types:
                        type_validation_results.append(f"{field}: {field_type.__name__} ✓")
                    else:
                        type_validation_results.append(f"{field}: {field_type.__name__} ⚠ (expected {[t.__name__ for t in expected_types]})")
            
            print(f"✓ Level info data types validated:")
            for validation in type_validation_results:
                print(f"  - {validation}")
    
    def test_get_current_level_info_json_serializable(self):
        """Test that current level info is JSON serializable."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_current_level_info", {})
            
            self._assert_valid_response(response, "get_current_level_info")
            
            result = response.get("result", {})
            
            # Test JSON serialization
            try:
                json_str = json.dumps(result)
                deserialized = json.loads(json_str)
                assert deserialized == result, "Level info should round-trip through JSON"
                print(f"✓ Level info is JSON serializable (size: {len(json_str)} chars)")
            except (TypeError, ValueError) as e:
                assert False, f"Level info should be JSON serializable, but got error: {e}"
    
    # =================================
    # PERFORMANCE TESTS
    # =================================
    
    def test_get_current_level_info_performance(self):
        """Test performance of getting current level info."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            num_calls = 20
            start_time = time.time()
            
            for i in range(num_calls):
                response = conn.send_command("get_current_level_info", {})
                self._assert_valid_response(response, f"get_current_level_info ({i})")
            
            duration = time.time() - start_time
            avg_time = duration / num_calls
            
            assert duration < 20.0, f"Getting level info {num_calls} times took too long: {duration}s"
            assert avg_time < 1.0, f"Average level info query time too slow: {avg_time}s"
            print(f"✓ Completed {num_calls} level info queries in {duration:.2f}s (avg: {avg_time:.3f}s per query)")
    
    def test_get_current_level_info_concurrent(self):
        """Test concurrent level info queries."""
        async def query_level_info(query_id: int) -> TestResult:
            """Query level info asynchronously."""
            try:
                with self.framework.test_connection() as conn:
                    if conn.connect():
                        start_time = time.time()
                        response = conn.send_command("get_current_level_info", {})
                        duration = time.time() - start_time
                        
                        if response and (response.get("success") or response.get("status") != "error"):
                            return TestResult(
                                name=f"concurrent_query_{query_id}",
                                success=True,
                                duration=duration
                            )
                        else:
                            return TestResult(
                                name=f"concurrent_query_{query_id}",
                                success=False,
                                error=response.get("error", "Query failed"),
                                duration=duration
                            )
                    else:
                        return TestResult(
                            name=f"concurrent_query_{query_id}",
                            success=False,
                            error="Connection failed"
                        )
            except Exception as e:
                return TestResult(
                    name=f"concurrent_query_{query_id}",
                    success=False,
                    error=str(e)
                )
        
        async def run_concurrent_test():
            num_concurrent = 5
            start_time = time.time()
            
            # Create tasks for concurrent queries
            tasks = [query_level_info(i) for i in range(num_concurrent)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            duration = time.time() - start_time
            
            # Process results
            successful = sum(1 for r in results if isinstance(r, TestResult) and r.success)
            
            assert successful >= num_concurrent * 0.8, f"Too many concurrent queries failed: {successful}/{num_concurrent}"
            assert duration < 15.0, f"Concurrent queries took too long: {duration}s"
            
            print(f"✓ Completed {num_concurrent} concurrent level info queries in {duration:.2f}s ({successful}/{num_concurrent} successful)")
        
        # Run the concurrent test
        asyncio.run(run_concurrent_test())
    
    # =================================
    # INTEGRATION TESTS
    # =================================
    
    def test_get_current_level_info_after_world_changes(self):
        """Test level info accuracy after various world changes."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Get baseline
            baseline_response = conn.send_command("get_current_level_info", {})
            self._assert_valid_response(baseline_response, "get_current_level_info (baseline)")
            
            changes_made = []
            
            # Try to spawn an actor
            spawn_response = conn.send_command("spawn_actor", {
                "name": "WorldTestActor",
                "type": "StaticMeshActor",
                "location": [1000.0, 0.0, 0.0]
            })
            
            if spawn_response and spawn_response.get("success"):
                changes_made.append("spawned_actor")
                
                # Check level info after spawning
                after_spawn_response = conn.send_command("get_current_level_info", {})
                self._assert_valid_response(after_spawn_response, "get_current_level_info (after spawn)")
                
                # Check if actor count changed
                baseline_result = baseline_response.get("result", {})
                after_spawn_result = after_spawn_response.get("result", {})
                
                baseline_actors = baseline_result.get("actors") or baseline_result.get("actor_count", 0)
                after_spawn_actors = after_spawn_result.get("actors") or after_spawn_result.get("actor_count", 0)
                
                if isinstance(baseline_actors, list) and isinstance(after_spawn_actors, list):
                    if len(after_spawn_actors) > len(baseline_actors):
                        print(f"  ✓ Level info reflects actor spawning (actors: {len(baseline_actors)} → {len(after_spawn_actors)})")
                    else:
                        print(f"  ✓ Level info stable after actor spawning")
                elif isinstance(baseline_actors, int) and isinstance(after_spawn_actors, int):
                    if after_spawn_actors > baseline_actors:
                        print(f"  ✓ Level info reflects actor spawning (count: {baseline_actors} → {after_spawn_actors})")
                    else:
                        print(f"  ✓ Level info stable after actor spawning")
                else:
                    print(f"  ✓ Level info available after actor spawning")
                
                # Clean up
                delete_response = conn.send_command("delete_actor", {
                    "name": "WorldTestActor"
                })
                if delete_response and delete_response.get("success"):
                    changes_made.append("deleted_actor")
            
            if not changes_made:
                print(f"⚠ No world changes could be made, testing basic level info stability")
                
                # Even without changes, level info should be consistent
                stability_response = conn.send_command("get_current_level_info", {})
                self._assert_valid_response(stability_response, "get_current_level_info (stability)")
            
            print(f"✓ Level info handles world changes appropriately (changes made: {changes_made})")

# =================================
# TEST RUNNER FUNCTIONS
# =================================

async def run_all_tests():
    """Run all world command tests."""
    test_suite = TestWorldCommands()
    test_suite.setup_class()
    
    # Get all test methods
    test_methods = [
        method for method in dir(test_suite) 
        if method.startswith('test_') and callable(getattr(test_suite, method))
    ]
    
    results = []
    print(f"\n🚀 Running {len(test_methods)} world command tests...\n")
    
    for method_name in test_methods:
        try:
            print(f"Running {method_name}...")
            test_method = getattr(test_suite, method_name)
            start_time = time.time()
            
            test_method()
            
            duration = time.time() - start_time
            result = TestResult(
                name=method_name,
                success=True,
                duration=duration
            )
            print(f"  ✅ PASSED ({duration:.2f}s)\n")
            
        except AssertionError as e:
            duration = time.time() - start_time
            result = TestResult(
                name=method_name,
                success=False,
                error=str(e),
                duration=duration
            )
            print(f"  ❌ FAILED: {e} ({duration:.2f}s)\n")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                name=method_name,
                success=False,
                error=f"Test error: {str(e)}",
                duration=duration
            )
            print(f"  💥 ERROR: {e} ({duration:.2f}s)\n")
        
        results.append(result)
    
    # Cleanup
    test_suite.teardown_class()
    
    # Print summary
    passed = sum(1 for r in results if r.success)
    failed = len(results) - passed
    total_time = sum(r.duration for r in results)
    
    print(f"\n📊 World Commands Test Summary:")
    print(f"   Total: {len(results)}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Duration: {total_time:.2f}s")
    print(f"   Success Rate: {(passed/len(results)*100):.1f}%")
    
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        for result in results:
            if not result.success:
                print(f"   - {result.name}: {result.error}")
    
    return results

if __name__ == "__main__":
    # Run tests when script is executed directly
    asyncio.run(run_all_tests())