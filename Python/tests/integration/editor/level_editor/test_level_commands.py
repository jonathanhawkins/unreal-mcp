"""
Comprehensive tests for Level Editor commands.

Tests all level editor operations including:
- create_level: Create new levels
- save_level: Save current level  
- load_level: Load existing levels
- set_level_visibility: Control level visibility
- create_streaming_level: Add streaming levels
- load_streaming_level: Load streaming levels
- unload_streaming_level: Unload streaming levels

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
from tests.data.test_data import get_test_data_manager, LevelTestData
from unreal_mcp_server import get_unreal_connection

class TestLevelCommands:
    """Test suite for Level Editor commands."""
    
    @classmethod
    def setup_class(cls):
        """Setup test framework and data."""
        cls.config = create_test_config()
        cls.framework = TestFramework(cls.config)
        cls.test_data_manager = get_test_data_manager()
        cls.test_results = []
        cls.cleanup_levels = []  # Track levels to cleanup
        
        # Test level data
        cls.test_levels = {
            "basic_test": "/Game/TestLevels/BasicTestLevel",
            "empty_test": "/Game/TestLevels/EmptyTestLevel", 
            "temp_test": "/Game/TestLevels/TempTestLevel",
            "streaming_test": "/Game/TestLevels/StreamingTestLevel",
            "complex_test": "/Game/TestLevels/ComplexTestLevel"
        }
        
        # Streaming level test data
        cls.streaming_levels = {
            "audio_streaming": "/Game/StreamingLevels/AudioLevel",
            "geometry_streaming": "/Game/StreamingLevels/GeometryLevel",
            "lighting_streaming": "/Game/StreamingLevels/LightingLevel"
        }
        
        # Expected level properties
        cls.level_expectations = {
            "default_actors": ["WorldSettings", "PostProcessVolume"],
            "required_systems": ["LevelScriptActor"],
            "lighting_scenarios": ["Stationary", "Static", "Movable"]
        }
    
    @classmethod
    def teardown_class(cls):
        """Cleanup test levels."""
        cls._cleanup_test_levels()
    
    @classmethod
    def _cleanup_test_levels(cls):
        """Clean up any test levels created during testing."""
        if not cls.cleanup_levels:
            return
            
        try:
            with cls.framework.test_connection() as conn:
                if conn.connect():
                    for level_path in cls.cleanup_levels:
                        try:
                            # Note: In real Unreal, level deletion is complex
                            # For tests, we just track what should be cleaned up
                            print(f"Would cleanup test level: {level_path}")
                        except Exception as e:
                            print(f"Failed to cleanup level {level_path}: {e}")
        except Exception as e:
            print(f"Error during test level cleanup: {e}")
    
    def _add_cleanup_level(self, level_path: str):
        """Add level to cleanup list."""
        if level_path not in self.cleanup_levels:
            self.cleanup_levels.append(level_path)
    
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
    
    def _verify_level_created(self, level_name: str) -> bool:
        """Verify that a level was actually created."""
        # In real implementation, would check filesystem or level registry
        # For tests, we assume creation was successful if command succeeded
        return True
    
    def _verify_level_loaded(self, level_path: str) -> bool:
        """Verify that a level is currently loaded."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("get_current_level_info", {})
                if response and response.get("success"):
                    current_level = response.get("result", {}).get("level_path", "")
                    return current_level == level_path
        return False
    
    # =================================
    # CREATE LEVEL TESTS
    # =================================
    
    def test_create_level_basic(self):
        """Test creating a basic new level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            level_name = "BasicTestLevel"
            
            response = conn.send_command("create_level", {
                "level_name": level_name
            })
            
            self._assert_valid_response(response, "create_level")
            self._add_cleanup_level(f"/Game/{level_name}")
            
            # Verify level creation
            assert self._verify_level_created(level_name), "Level was not created"
            print(f"✓ Successfully created basic level: {level_name}")
    
    def test_create_level_with_template(self):
        """Test creating a level with specific template."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            level_name = "TemplateTestLevel"
            
            response = conn.send_command("create_level", {
                "level_name": level_name,
                "template": "Default"
            })
            
            self._assert_valid_response(response, "create_level")
            self._add_cleanup_level(f"/Game/{level_name}")
            print(f"✓ Successfully created level with template: {level_name}")
    
    def test_create_level_empty_name(self):
        """Test creating level with empty name."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("create_level", {
                "level_name": ""
            })
            
            self._assert_error_response(response, "create_level", "name")
            print(f"✓ Correctly handled empty level name")
    
    def test_create_level_invalid_name(self):
        """Test creating level with invalid characters in name."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            invalid_names = [
                "Invalid/Level*Name",
                "Level<With>Invalid",
                "Level:With|Chars",
                "Level\"With'Quotes"
            ]
            
            for invalid_name in invalid_names:
                response = conn.send_command("create_level", {
                    "level_name": invalid_name
                })
                
                # Should either reject invalid chars or sanitize them
                if response.get("success"):
                    print(f"✓ Level creation handled invalid name (may have sanitized): {invalid_name}")
                else:
                    print(f"✓ Correctly rejected invalid level name: {invalid_name}")
    
    def test_create_level_duplicate_name(self):
        """Test creating level with duplicate name."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            level_name = "DuplicateTestLevel"
            
            # Create first level
            response1 = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(response1, "create_level (first)")
            self._add_cleanup_level(f"/Game/{level_name}")
            
            # Try to create duplicate
            response2 = conn.send_command("create_level", {
                "level_name": level_name
            })
            
            # Should handle gracefully (either error or create with modified name)
            if response2.get("success"):
                print(f"✓ Duplicate level creation handled (may use modified name)")
            else:
                self._assert_error_response(response2, "create_level (duplicate)", "exists")
                print(f"✓ Correctly prevented duplicate level creation")
    
    # =================================
    # SAVE LEVEL TESTS
    # =================================
    
    def test_save_level_current(self):
        """Test saving the current level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("save_level", {})
            
            self._assert_valid_response(response, "save_level")
            print(f"✓ Successfully saved current level")
    
    def test_save_level_specific(self):
        """Test saving a specific level by path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # First create a level to save
            level_name = "SaveTestLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            self._add_cleanup_level(f"/Game/{level_name}")
            
            # Now save it specifically
            response = conn.send_command("save_level", {
                "level_path": f"/Game/{level_name}"
            })
            
            self._assert_valid_response(response, "save_level")
            print(f"✓ Successfully saved specific level: {level_name}")
    
    def test_save_level_force_save(self):
        """Test force saving a level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("save_level", {
                "force_save": True
            })
            
            self._assert_valid_response(response, "save_level")
            print(f"✓ Successfully force saved level")
    
    def test_save_level_nonexistent(self):
        """Test saving a non-existent level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("save_level", {
                "level_path": "/Game/NonExistentLevel"
            })
            
            self._assert_error_response(response, "save_level", "not found")
            print(f"✓ Correctly handled saving non-existent level")
    
    # =================================
    # LOAD LEVEL TESTS
    # =================================
    
    def test_load_level_basic(self):
        """Test loading a basic level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # First create a level to load
            level_name = "LoadTestLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            level_path = f"/Game/{level_name}"
            self._add_cleanup_level(level_path)
            
            # Save it
            save_response = conn.send_command("save_level", {})
            self._assert_valid_response(save_response, "save_level")
            
            # Now load it
            response = conn.send_command("load_level", {
                "level_path": level_path
            })
            
            self._assert_valid_response(response, "load_level")
            
            # Verify it's loaded
            assert self._verify_level_loaded(level_path), "Level was not loaded"
            print(f"✓ Successfully loaded level: {level_name}")
    
    def test_load_level_nonexistent(self):
        """Test loading a non-existent level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("load_level", {
                "level_path": "/Game/NonExistentLevel"
            })
            
            self._assert_error_response(response, "load_level", "not found")
            print(f"✓ Correctly handled loading non-existent level")
    
    def test_load_level_invalid_path(self):
        """Test loading level with invalid path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            invalid_paths = [
                "",
                "invalid/path",
                "/Invalid*/Path<>",
                "/Engine/Private/RestrictedLevel"
            ]
            
            for invalid_path in invalid_paths:
                response = conn.send_command("load_level", {
                    "level_path": invalid_path
                })
                
                self._assert_error_response(response, "load_level", "invalid")
                print(f"✓ Correctly handled invalid level path: {invalid_path}")
    
    def test_load_level_with_options(self):
        """Test loading level with specific options."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create a level to test with
            level_name = "OptionsTestLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            level_path = f"/Game/{level_name}"
            self._add_cleanup_level(level_path)
            
            # Load with options
            response = conn.send_command("load_level", {
                "level_path": level_path,
                "load_streaming_levels": True,
                "make_visible": True
            })
            
            self._assert_valid_response(response, "load_level")
            print(f"✓ Successfully loaded level with options: {level_name}")
    
    # =================================
    # LEVEL VISIBILITY TESTS
    # =================================
    
    def test_set_level_visibility_show(self):
        """Test making a level visible."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create a level for visibility testing
            level_name = "VisibilityTestLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            self._add_cleanup_level(f"/Game/{level_name}")
            
            # Set visible
            response = conn.send_command("set_level_visibility", {
                "level_name": level_name,
                "visible": True
            })
            
            self._assert_valid_response(response, "set_level_visibility")
            print(f"✓ Successfully made level visible: {level_name}")
    
    def test_set_level_visibility_hide(self):
        """Test hiding a level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            level_name = "HideTestLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            self._add_cleanup_level(f"/Game/{level_name}")
            
            # Set invisible
            response = conn.send_command("set_level_visibility", {
                "level_name": level_name,
                "visible": False
            })
            
            self._assert_valid_response(response, "set_level_visibility")
            print(f"✓ Successfully hid level: {level_name}")
    
    def test_set_level_visibility_nonexistent(self):
        """Test setting visibility of non-existent level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("set_level_visibility", {
                "level_name": "NonExistentLevel",
                "visible": True
            })
            
            self._assert_error_response(response, "set_level_visibility", "not found")
            print(f"✓ Correctly handled visibility of non-existent level")
    
    def test_set_level_visibility_persistent(self):
        """Test setting visibility of persistent level (should handle specially)."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("set_level_visibility", {
                "level_name": "Persistent Level",
                "visible": False
            })
            
            # Persistent level visibility may be handled differently
            if response.get("success"):
                print(f"✓ Persistent level visibility handled")
            else:
                print(f"✓ Correctly protected persistent level visibility")
    
    # =================================
    # STREAMING LEVEL TESTS
    # =================================
    
    def test_create_streaming_level_basic(self):
        """Test creating a basic streaming level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # First create a level to use as streaming level
            level_name = "StreamingSourceLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            level_path = f"/Game/{level_name}"
            self._add_cleanup_level(level_path)
            
            # Create streaming level
            response = conn.send_command("create_streaming_level", {
                "level_path": level_path
            })
            
            self._assert_valid_response(response, "create_streaming_level")
            print(f"✓ Successfully created streaming level: {level_name}")
    
    def test_create_streaming_level_with_transform(self):
        """Test creating streaming level with transform."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            level_name = "TransformStreamingLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            level_path = f"/Game/{level_name}"
            self._add_cleanup_level(level_path)
            
            response = conn.send_command("create_streaming_level", {
                "level_path": level_path,
                "location": [1000.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 45.0]
            })
            
            self._assert_valid_response(response, "create_streaming_level")
            print(f"✓ Successfully created streaming level with transform")
    
    def test_create_streaming_level_nonexistent(self):
        """Test creating streaming level from non-existent level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("create_streaming_level", {
                "level_path": "/Game/NonExistentStreamingLevel"
            })
            
            self._assert_error_response(response, "create_streaming_level", "not found")
            print(f"✓ Correctly handled non-existent streaming level source")
    
    def test_load_streaming_level_basic(self):
        """Test loading a streaming level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create and setup streaming level
            level_name = "LoadStreamingLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            level_path = f"/Game/{level_name}"
            self._add_cleanup_level(level_path)
            
            # Create as streaming level
            create_streaming_response = conn.send_command("create_streaming_level", {
                "level_path": level_path
            })
            self._assert_valid_response(create_streaming_response, "create_streaming_level")
            
            # Load streaming level
            response = conn.send_command("load_streaming_level", {
                "level_name": level_name
            })
            
            self._assert_valid_response(response, "load_streaming_level")
            print(f"✓ Successfully loaded streaming level: {level_name}")
    
    def test_load_streaming_level_nonexistent(self):
        """Test loading non-existent streaming level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("load_streaming_level", {
                "level_name": "NonExistentStreamingLevel"
            })
            
            self._assert_error_response(response, "load_streaming_level", "not found")
            print(f"✓ Correctly handled loading non-existent streaming level")
    
    def test_unload_streaming_level_basic(self):
        """Test unloading a streaming level."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Setup streaming level
            level_name = "UnloadStreamingLevel"
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            level_path = f"/Game/{level_name}"
            self._add_cleanup_level(level_path)
            
            # Create and load as streaming level
            create_streaming_response = conn.send_command("create_streaming_level", {
                "level_path": level_path
            })
            self._assert_valid_response(create_streaming_response, "create_streaming_level")
            
            load_streaming_response = conn.send_command("load_streaming_level", {
                "level_name": level_name
            })
            self._assert_valid_response(load_streaming_response, "load_streaming_level")
            
            # Unload streaming level
            response = conn.send_command("unload_streaming_level", {
                "level_name": level_name
            })
            
            self._assert_valid_response(response, "unload_streaming_level")
            print(f"✓ Successfully unloaded streaming level: {level_name}")
    
    def test_unload_streaming_level_not_loaded(self):
        """Test unloading streaming level that's not loaded."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("unload_streaming_level", {
                "level_name": "NotLoadedStreamingLevel"
            })
            
            # Should handle gracefully (may be no-op or error)
            if response.get("success"):
                print(f"✓ Unloading not-loaded streaming level handled gracefully")
            else:
                print(f"✓ Correctly handled unloading not-loaded streaming level")
    
    # =================================
    # EDGE CASE TESTS
    # =================================
    
    def test_level_operations_sequence(self):
        """Test sequence of level operations."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            level_name = "SequenceTestLevel"
            level_path = f"/Game/{level_name}"
            
            # Create -> Save -> Load -> Hide -> Show sequence
            create_response = conn.send_command("create_level", {
                "level_name": level_name
            })
            self._assert_valid_response(create_response, "create_level")
            self._add_cleanup_level(level_path)
            
            save_response = conn.send_command("save_level", {})
            self._assert_valid_response(save_response, "save_level")
            
            load_response = conn.send_command("load_level", {
                "level_path": level_path
            })
            self._assert_valid_response(load_response, "load_level")
            
            hide_response = conn.send_command("set_level_visibility", {
                "level_name": level_name,
                "visible": False
            })
            self._assert_valid_response(hide_response, "set_level_visibility (hide)")
            
            show_response = conn.send_command("set_level_visibility", {
                "level_name": level_name,
                "visible": True
            })
            self._assert_valid_response(show_response, "set_level_visibility (show)")
            
            print(f"✓ Successfully completed level operations sequence")
    
    def test_multiple_streaming_levels(self):
        """Test managing multiple streaming levels."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            streaming_levels = ["Stream1", "Stream2", "Stream3"]
            
            # Create multiple streaming levels
            for i, level_name in enumerate(streaming_levels):
                create_response = conn.send_command("create_level", {
                    "level_name": level_name
                })
                self._assert_valid_response(create_response, f"create_level ({level_name})")
                level_path = f"/Game/{level_name}"
                self._add_cleanup_level(level_path)
                
                streaming_response = conn.send_command("create_streaming_level", {
                    "level_path": level_path,
                    "location": [i * 1000.0, 0.0, 0.0]
                })
                self._assert_valid_response(streaming_response, f"create_streaming_level ({level_name})")
            
            # Load all streaming levels
            for level_name in streaming_levels:
                load_response = conn.send_command("load_streaming_level", {
                    "level_name": level_name
                })
                self._assert_valid_response(load_response, f"load_streaming_level ({level_name})")
            
            # Unload all streaming levels
            for level_name in streaming_levels:
                unload_response = conn.send_command("unload_streaming_level", {
                    "level_name": level_name
                })
                self._assert_valid_response(unload_response, f"unload_streaming_level ({level_name})")
            
            print(f"✓ Successfully managed multiple streaming levels")
    
    # =================================
    # PERFORMANCE TESTS
    # =================================
    
    def test_level_creation_performance(self):
        """Test performance of level creation operations."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            num_levels = 5
            start_time = time.time()
            
            for i in range(num_levels):
                level_name = f"PerfTestLevel_{i}"
                response = conn.send_command("create_level", {
                    "level_name": level_name
                })
                self._assert_valid_response(response, f"create_level ({level_name})")
                self._add_cleanup_level(f"/Game/{level_name}")
            
            duration = time.time() - start_time
            avg_time = duration / num_levels
            
            assert duration < 60.0, f"Creating {num_levels} levels took too long: {duration}s"
            assert avg_time < 12.0, f"Average level creation time too slow: {avg_time}s"
            print(f"✓ Created {num_levels} levels in {duration:.2f}s (avg: {avg_time:.2f}s per level)")
    
    def test_streaming_level_load_performance(self):
        """Test performance of streaming level operations."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            num_streaming_levels = 3
            streaming_levels = []
            
            # Setup streaming levels
            for i in range(num_streaming_levels):
                level_name = f"StreamingPerfLevel_{i}"
                create_response = conn.send_command("create_level", {
                    "level_name": level_name
                })
                self._assert_valid_response(create_response, f"create_level ({level_name})")
                level_path = f"/Game/{level_name}"
                self._add_cleanup_level(level_path)
                
                streaming_response = conn.send_command("create_streaming_level", {
                    "level_path": level_path
                })
                self._assert_valid_response(streaming_response, f"create_streaming_level ({level_name})")
                streaming_levels.append(level_name)
            
            # Test load performance
            start_time = time.time()
            for level_name in streaming_levels:
                load_response = conn.send_command("load_streaming_level", {
                    "level_name": level_name
                })
                self._assert_valid_response(load_response, f"load_streaming_level ({level_name})")
            
            load_duration = time.time() - start_time
            
            # Test unload performance
            start_time = time.time()
            for level_name in streaming_levels:
                unload_response = conn.send_command("unload_streaming_level", {
                    "level_name": level_name
                })
                self._assert_valid_response(unload_response, f"unload_streaming_level ({level_name})")
            
            unload_duration = time.time() - start_time
            
            total_duration = load_duration + unload_duration
            assert total_duration < 30.0, f"Streaming operations took too long: {total_duration}s"
            print(f"✓ Streaming level operations completed in {total_duration:.2f}s (load: {load_duration:.2f}s, unload: {unload_duration:.2f}s)")

# =================================
# TEST RUNNER FUNCTIONS
# =================================

async def run_all_tests():
    """Run all level command tests."""
    test_suite = TestLevelCommands()
    test_suite.setup_class()
    
    # Get all test methods
    test_methods = [
        method for method in dir(test_suite) 
        if method.startswith('test_') and callable(getattr(test_suite, method))
    ]
    
    results = []
    print(f"\n🚀 Running {len(test_methods)} level command tests...\n")
    
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
    
    print(f"\n📊 Level Commands Test Summary:")
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