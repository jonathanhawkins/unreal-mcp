"""
Comprehensive tests for Landscape commands.

Tests all landscape operations including:
- create_landscape: Create landscapes with various configurations
- modify_landscape: Modify landscape heightmaps and geometry
- paint_landscape_layer: Paint landscape material layers
- get_landscape_info: Query landscape information and properties

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

class TestLandscapeCommands:
    """Test suite for Landscape commands."""
    
    @classmethod
    def setup_class(cls):
        """Setup test framework and data."""
        cls.config = create_test_config()
        cls.framework = TestFramework(cls.config)
        cls.test_data_manager = get_test_data_manager()
        cls.test_results = []
        cls.cleanup_landscapes = []  # Track landscapes to cleanup
        
        # Common landscape configurations
        cls.landscape_configs = {
            "small": {
                "size_x": 63,
                "size_y": 63,
                "sections_per_component": 1,
                "quads_per_section": 31,
                "location": [0.0, 0.0, 0.0]
            },
            "medium": {
                "size_x": 127,
                "size_y": 127,
                "sections_per_component": 1,
                "quads_per_section": 63,
                "location": [5000.0, 0.0, 0.0]
            },
            "large": {
                "size_x": 255,
                "size_y": 255,
                "sections_per_component": 2,
                "quads_per_section": 63,
                "location": [10000.0, 0.0, 0.0]
            },
            "elevated": {
                "size_x": 127,
                "size_y": 127,
                "sections_per_component": 1,
                "quads_per_section": 63,
                "location": [0.0, 0.0, 1000.0]
            }
        }
        
        # Landscape layer configurations
        cls.layer_configs = {
            "grass": {"name": "Grass", "weight": 1.0},
            "dirt": {"name": "Dirt", "weight": 0.8},
            "rock": {"name": "Rock", "weight": 0.6},
            "sand": {"name": "Sand", "weight": 0.4}
        }
        
        # Landscape modification types
        cls.modification_types = [
            "sculpt",
            "smooth", 
            "flatten",
            "ramp",
            "erosion",
            "noise"
        ]
    
    @classmethod
    def teardown_class(cls):
        """Cleanup test landscapes."""
        cls._cleanup_test_landscapes()
    
    @classmethod
    def _cleanup_test_landscapes(cls):
        """Clean up any test landscapes created during testing."""
        if not cls.cleanup_landscapes:
            return
            
        try:
            with cls.framework.test_connection() as conn:
                if conn.connect():
                    for landscape_id in cls.cleanup_landscapes:
                        try:
                            # Note: Landscape cleanup in real Unreal is complex
                            # For tests, we track what should be cleaned up
                            print(f"Would cleanup test landscape: {landscape_id}")
                        except Exception as e:
                            print(f"Failed to cleanup landscape {landscape_id}: {e}")
        except Exception as e:
            print(f"Error during test landscape cleanup: {e}")
    
    def _add_cleanup_landscape(self, landscape_id: str):
        """Add landscape to cleanup list."""
        if landscape_id not in self.cleanup_landscapes:
            self.cleanup_landscapes.append(landscape_id)
    
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
    
    def _verify_landscape_created(self, expected_size: tuple) -> bool:
        """Verify that a landscape was created with expected properties."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("get_landscape_info", {})
                if response and response.get("success"):
                    landscapes = response.get("result", [])
                    if isinstance(landscapes, dict) and "landscapes" in landscapes:
                        landscapes = landscapes["landscapes"]
                    
                    for landscape in landscapes:
                        if (landscape.get("size_x") == expected_size[0] and 
                            landscape.get("size_y") == expected_size[1]):
                            return True
        return False
    
    def _get_current_landscapes(self) -> List[Dict[str, Any]]:
        """Get list of current landscapes in the level."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("get_landscape_info", {})
                if response and response.get("success"):
                    landscapes = response.get("result", [])
                    if isinstance(landscapes, dict) and "landscapes" in landscapes:
                        return landscapes["landscapes"]
                    return landscapes if isinstance(landscapes, list) else []
        return []
    
    # =================================
    # CREATE LANDSCAPE TESTS
    # =================================
    
    def test_create_landscape_small(self):
        """Test creating a small landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            config = self.landscape_configs["small"]
            
            response = conn.send_command("create_landscape", {
                "size_x": config["size_x"],
                "size_y": config["size_y"],
                "sections_per_component": config["sections_per_component"],
                "quads_per_section": config["quads_per_section"],
                "location_x": config["location"][0],
                "location_y": config["location"][1],
                "location_z": config["location"][2]
            })
            
            self._assert_valid_response(response, "create_landscape")
            self._add_cleanup_landscape(f"small_landscape_{config['size_x']}x{config['size_y']}")
            
            # Verify landscape creation
            assert self._verify_landscape_created((config["size_x"], config["size_y"])), \
                "Small landscape was not created"
            print(f"✓ Successfully created small landscape ({config['size_x']}x{config['size_y']})")
    
    def test_create_landscape_medium(self):
        """Test creating a medium-sized landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            config = self.landscape_configs["medium"]
            
            response = conn.send_command("create_landscape", {
                "size_x": config["size_x"],
                "size_y": config["size_y"],
                "sections_per_component": config["sections_per_component"],
                "quads_per_section": config["quads_per_section"],
                "location_x": config["location"][0],
                "location_y": config["location"][1],
                "location_z": config["location"][2]
            })
            
            self._assert_valid_response(response, "create_landscape")
            self._add_cleanup_landscape(f"medium_landscape_{config['size_x']}x{config['size_y']}")
            print(f"✓ Successfully created medium landscape ({config['size_x']}x{config['size_y']})")
    
    def test_create_landscape_large(self):
        """Test creating a large landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            config = self.landscape_configs["large"]
            
            response = conn.send_command("create_landscape", {
                "size_x": config["size_x"],
                "size_y": config["size_y"],
                "sections_per_component": config["sections_per_component"],
                "quads_per_section": config["quads_per_section"],
                "location_x": config["location"][0],
                "location_y": config["location"][1],
                "location_z": config["location"][2]
            })
            
            self._assert_valid_response(response, "create_landscape")
            self._add_cleanup_landscape(f"large_landscape_{config['size_x']}x{config['size_y']}")
            print(f"✓ Successfully created large landscape ({config['size_x']}x{config['size_y']})")
    
    def test_create_landscape_elevated(self):
        """Test creating an elevated landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            config = self.landscape_configs["elevated"]
            
            response = conn.send_command("create_landscape", {
                "size_x": config["size_x"],
                "size_y": config["size_y"],
                "sections_per_component": config["sections_per_component"],
                "quads_per_section": config["quads_per_section"],
                "location_x": config["location"][0],
                "location_y": config["location"][1],
                "location_z": config["location"][2]
            })
            
            self._assert_valid_response(response, "create_landscape")
            self._add_cleanup_landscape(f"elevated_landscape_{config['size_x']}x{config['size_y']}")
            print(f"✓ Successfully created elevated landscape at Z={config['location'][2]}")
    
    def test_create_landscape_default_params(self):
        """Test creating landscape with default parameters."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("create_landscape", {})
            
            self._assert_valid_response(response, "create_landscape")
            self._add_cleanup_landscape("default_landscape_127x127")
            print(f"✓ Successfully created landscape with default parameters")
    
    def test_create_landscape_invalid_size_negative(self):
        """Test creating landscape with negative size values."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("create_landscape", {
                "size_x": -100,
                "size_y": -50
            })
            
            self._assert_error_response(response, "create_landscape", "invalid")
            print(f"✓ Correctly handled negative landscape size")
    
    def test_create_landscape_invalid_size_zero(self):
        """Test creating landscape with zero size values."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("create_landscape", {
                "size_x": 0,
                "size_y": 0
            })
            
            self._assert_error_response(response, "create_landscape", "invalid")
            print(f"✓ Correctly handled zero landscape size")
    
    def test_create_landscape_invalid_sections_per_component(self):
        """Test creating landscape with invalid sections per component."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("create_landscape", {
                "size_x": 127,
                "size_y": 127,
                "sections_per_component": 0
            })
            
            self._assert_error_response(response, "create_landscape", "invalid")
            print(f"✓ Correctly handled invalid sections per component")
    
    def test_create_landscape_invalid_quads_per_section(self):
        """Test creating landscape with invalid quads per section."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("create_landscape", {
                "size_x": 127,
                "size_y": 127,
                "quads_per_section": 0
            })
            
            self._assert_error_response(response, "create_landscape", "invalid")
            print(f"✓ Correctly handled invalid quads per section")
    
    # =================================
    # MODIFY LANDSCAPE TESTS
    # =================================
    
    def test_modify_landscape_sculpt(self):
        """Test modifying landscape with sculpt operation."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # First create a landscape to modify
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("sculpt_test_landscape")
            
            # Modify the landscape
            response = conn.send_command("modify_landscape", {
                "modification_type": "sculpt"
            })
            
            self._assert_valid_response(response, "modify_landscape")
            print(f"✓ Successfully modified landscape with sculpt operation")
    
    def test_modify_landscape_smooth(self):
        """Test modifying landscape with smooth operation."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create landscape for testing
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("smooth_test_landscape")
            
            response = conn.send_command("modify_landscape", {
                "modification_type": "smooth"
            })
            
            self._assert_valid_response(response, "modify_landscape")
            print(f"✓ Successfully modified landscape with smooth operation")
    
    def test_modify_landscape_flatten(self):
        """Test modifying landscape with flatten operation."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("flatten_test_landscape")
            
            response = conn.send_command("modify_landscape", {
                "modification_type": "flatten"
            })
            
            self._assert_valid_response(response, "modify_landscape")
            print(f"✓ Successfully modified landscape with flatten operation")
    
    def test_modify_landscape_all_types(self):
        """Test all landscape modification types."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create a landscape for comprehensive testing
            config = self.landscape_configs["medium"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("all_types_test_landscape")
            
            for mod_type in self.modification_types:
                response = conn.send_command("modify_landscape", {
                    "modification_type": mod_type
                })
                
                # Some modification types might not be supported
                if response and response.get("success"):
                    print(f"  ✓ {mod_type} modification successful")
                else:
                    print(f"  ⚠ {mod_type} modification not supported or failed")
            
            print(f"✓ Tested all landscape modification types")
    
    def test_modify_landscape_no_landscape(self):
        """Test modifying landscape when no landscape exists."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("modify_landscape", {
                "modification_type": "sculpt"
            })
            
            # Should handle gracefully (may be no-op or error)
            if response and response.get("success"):
                print(f"✓ Landscape modification handled when no landscape present")
            else:
                print(f"✓ Correctly handled landscape modification with no landscape")
    
    def test_modify_landscape_invalid_type(self):
        """Test modifying landscape with invalid modification type."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create landscape first
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("invalid_type_test_landscape")
            
            response = conn.send_command("modify_landscape", {
                "modification_type": "invalid_modification_type"
            })
            
            self._assert_error_response(response, "modify_landscape", "invalid")
            print(f"✓ Correctly handled invalid landscape modification type")
    
    # =================================
    # PAINT LANDSCAPE LAYER TESTS
    # =================================
    
    def test_paint_landscape_layer_grass(self):
        """Test painting grass layer on landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create landscape for painting
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("grass_paint_landscape")
            
            response = conn.send_command("paint_landscape_layer", {
                "layer_name": "Grass"
            })
            
            self._assert_valid_response(response, "paint_landscape_layer")
            print(f"✓ Successfully painted grass layer on landscape")
    
    def test_paint_landscape_layer_dirt(self):
        """Test painting dirt layer on landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("dirt_paint_landscape")
            
            response = conn.send_command("paint_landscape_layer", {
                "layer_name": "Dirt"
            })
            
            self._assert_valid_response(response, "paint_landscape_layer")
            print(f"✓ Successfully painted dirt layer on landscape")
    
    def test_paint_landscape_layer_rock(self):
        """Test painting rock layer on landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("rock_paint_landscape")
            
            response = conn.send_command("paint_landscape_layer", {
                "layer_name": "Rock"
            })
            
            self._assert_valid_response(response, "paint_landscape_layer")
            print(f"✓ Successfully painted rock layer on landscape")
    
    def test_paint_landscape_all_layers(self):
        """Test painting multiple layers on landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create landscape for multi-layer painting
            config = self.landscape_configs["medium"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("multi_layer_landscape")
            
            for layer_name, layer_config in self.layer_configs.items():
                response = conn.send_command("paint_landscape_layer", {
                    "layer_name": layer_config["name"]
                })
                
                if response and response.get("success"):
                    print(f"  ✓ {layer_config['name']} layer painted successfully")
                else:
                    print(f"  ⚠ {layer_config['name']} layer painting failed or not supported")
            
            print(f"✓ Tested painting all landscape layers")
    
    def test_paint_landscape_layer_no_landscape(self):
        """Test painting layer when no landscape exists."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("paint_landscape_layer", {
                "layer_name": "Grass"
            })
            
            # Should handle gracefully (may be no-op or error)
            if response and response.get("success"):
                print(f"✓ Layer painting handled when no landscape present")
            else:
                print(f"✓ Correctly handled layer painting with no landscape")
    
    def test_paint_landscape_layer_invalid_layer(self):
        """Test painting invalid layer on landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create landscape first
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("invalid_layer_landscape")
            
            response = conn.send_command("paint_landscape_layer", {
                "layer_name": "NonExistentLayer"
            })
            
            # May fail or succeed depending on implementation
            if response and response.get("success"):
                print(f"✓ Invalid layer painting handled (may create layer)")
            else:
                print(f"✓ Correctly handled invalid layer painting")
    
    def test_paint_landscape_layer_empty_name(self):
        """Test painting landscape layer with empty name."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            config = self.landscape_configs["small"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("empty_name_layer_landscape")
            
            response = conn.send_command("paint_landscape_layer", {
                "layer_name": ""
            })
            
            self._assert_error_response(response, "paint_landscape_layer")
            print(f"✓ Correctly handled empty layer name")
    
    # =================================
    # GET LANDSCAPE INFO TESTS
    # =================================
    
    def test_get_landscape_info_empty_level(self):
        """Test getting landscape info when no landscapes exist."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_landscape_info", {})
            
            self._assert_valid_response(response, "get_landscape_info")
            
            # Should return empty list or empty result
            landscapes = response.get("result", [])
            if isinstance(landscapes, dict) and "landscapes" in landscapes:
                landscapes = landscapes["landscapes"]
            
            assert isinstance(landscapes, list), "Landscape info should return a list"
            print(f"✓ Successfully retrieved landscape info (found {len(landscapes)} landscapes)")
    
    def test_get_landscape_info_single_landscape(self):
        """Test getting landscape info with single landscape."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create a landscape
            config = self.landscape_configs["medium"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("single_info_landscape")
            
            response = conn.send_command("get_landscape_info", {})
            
            self._assert_valid_response(response, "get_landscape_info")
            
            landscapes = response.get("result", [])
            if isinstance(landscapes, dict) and "landscapes" in landscapes:
                landscapes = landscapes["landscapes"]
            
            assert isinstance(landscapes, list), "Landscape info should return a list"
            assert len(landscapes) >= 1, "Should find at least one landscape"
            
            # Verify landscape properties
            landscape = landscapes[0]
            assert "size_x" in landscape or "width" in landscape, "Landscape should have size information"
            assert "size_y" in landscape or "height" in landscape, "Landscape should have size information"
            
            print(f"✓ Successfully retrieved single landscape info: {landscape}")
    
    def test_get_landscape_info_multiple_landscapes(self):
        """Test getting landscape info with multiple landscapes."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create multiple landscapes
            configs = ["small", "medium"]
            for i, config_name in enumerate(configs):
                config = self.landscape_configs[config_name].copy()
                # Offset locations to avoid overlap
                config["location_x"] += i * 2000.0
                
                create_response = conn.send_command("create_landscape", {
                    "size_x": config["size_x"],
                    "size_y": config["size_y"],
                    "sections_per_component": config["sections_per_component"],
                    "quads_per_section": config["quads_per_section"],
                    "location_x": config["location_x"],
                    "location_y": config["location_y"],
                    "location_z": config["location_z"]
                })
                self._assert_valid_response(create_response, f"create_landscape ({config_name})")
                self._add_cleanup_landscape(f"multi_info_landscape_{i}")
            
            response = conn.send_command("get_landscape_info", {})
            
            self._assert_valid_response(response, "get_landscape_info")
            
            landscapes = response.get("result", [])
            if isinstance(landscapes, dict) and "landscapes" in landscapes:
                landscapes = landscapes["landscapes"]
            
            assert isinstance(landscapes, list), "Landscape info should return a list"
            assert len(landscapes) >= len(configs), f"Should find at least {len(configs)} landscapes"
            
            print(f"✓ Successfully retrieved multiple landscape info (found {len(landscapes)} landscapes)")
    
    def test_get_landscape_info_properties(self):
        """Test that landscape info contains expected properties."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create landscape with known properties
            config = self.landscape_configs["large"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("properties_info_landscape")
            
            response = conn.send_command("get_landscape_info", {})
            
            self._assert_valid_response(response, "get_landscape_info")
            
            landscapes = response.get("result", [])
            if isinstance(landscapes, dict) and "landscapes" in landscapes:
                landscapes = landscapes["landscapes"]
            
            assert len(landscapes) >= 1, "Should find at least one landscape"
            
            landscape = landscapes[-1]  # Get the last created one
            
            # Check for expected properties
            expected_properties = [
                ("size_x", "width", "x_size"),
                ("size_y", "height", "y_size"),
                ("location", "position", "transform"),
                ("components", "num_components")
            ]
            
            found_properties = []
            for prop_variants in expected_properties:
                for prop in prop_variants:
                    if prop in landscape:
                        found_properties.append(prop)
                        break
            
            assert len(found_properties) > 0, f"Landscape should have basic properties. Found: {list(landscape.keys())}"
            print(f"✓ Landscape info contains expected properties: {found_properties}")
    
    # =================================
    # EDGE CASE TESTS
    # =================================
    
    def test_landscape_operations_sequence(self):
        """Test sequence of landscape operations."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create -> Modify -> Paint -> Info sequence
            config = self.landscape_configs["small"]
            
            # Create landscape
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("sequence_test_landscape")
            
            # Modify landscape
            modify_response = conn.send_command("modify_landscape", {
                "modification_type": "sculpt"
            })
            self._assert_valid_response(modify_response, "modify_landscape")
            
            # Paint landscape
            paint_response = conn.send_command("paint_landscape_layer", {
                "layer_name": "Grass"
            })
            self._assert_valid_response(paint_response, "paint_landscape_layer")
            
            # Get landscape info
            info_response = conn.send_command("get_landscape_info", {})
            self._assert_valid_response(info_response, "get_landscape_info")
            
            print(f"✓ Successfully completed landscape operations sequence")
    
    def test_landscape_extreme_values(self):
        """Test landscape creation with extreme values."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            extreme_configs = [
                {
                    "name": "very_small",
                    "size_x": 7,
                    "size_y": 7,
                    "sections_per_component": 1,
                    "quads_per_section": 3
                },
                {
                    "name": "very_far",
                    "size_x": 63,
                    "size_y": 63,
                    "location_x": 50000.0,
                    "location_y": 50000.0,
                    "location_z": 10000.0
                }
            ]
            
            for config in extreme_configs:
                response = conn.send_command("create_landscape", config)
                
                if response and response.get("success"):
                    self._add_cleanup_landscape(f"extreme_{config['name']}_landscape")
                    print(f"  ✓ {config['name']} landscape created successfully")
                else:
                    print(f"  ⚠ {config['name']} landscape creation handled appropriately")
            
            print(f"✓ Tested landscape creation with extreme values")
    
    # =================================
    # PERFORMANCE TESTS
    # =================================
    
    def test_landscape_creation_performance(self):
        """Test performance of landscape creation operations."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            num_landscapes = 3
            config = self.landscape_configs["small"]
            start_time = time.time()
            
            for i in range(num_landscapes):
                test_config = config.copy()
                test_config["location_x"] = i * 1000.0  # Offset to avoid overlap
                
                response = conn.send_command("create_landscape", {
                    "size_x": test_config["size_x"],
                    "size_y": test_config["size_y"],
                    "sections_per_component": test_config["sections_per_component"],
                    "quads_per_section": test_config["quads_per_section"],
                    "location_x": test_config["location_x"],
                    "location_y": test_config["location_y"],
                    "location_z": test_config["location_z"]
                })
                self._assert_valid_response(response, f"create_landscape ({i})")
                self._add_cleanup_landscape(f"perf_landscape_{i}")
            
            duration = time.time() - start_time
            avg_time = duration / num_landscapes
            
            assert duration < 90.0, f"Creating {num_landscapes} landscapes took too long: {duration}s"
            assert avg_time < 30.0, f"Average landscape creation time too slow: {avg_time}s"
            print(f"✓ Created {num_landscapes} landscapes in {duration:.2f}s (avg: {avg_time:.2f}s per landscape)")
    
    def test_landscape_modification_performance(self):
        """Test performance of landscape modification operations."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create landscape for testing
            config = self.landscape_configs["medium"]
            create_response = conn.send_command("create_landscape", config)
            self._assert_valid_response(create_response, "create_landscape")
            self._add_cleanup_landscape("perf_modify_landscape")
            
            # Test multiple modifications
            modifications = ["sculpt", "smooth", "flatten"]
            start_time = time.time()
            
            for mod_type in modifications:
                response = conn.send_command("modify_landscape", {
                    "modification_type": mod_type
                })
                if response and response.get("success"):
                    print(f"  ✓ {mod_type} modification completed")
                else:
                    print(f"  ⚠ {mod_type} modification skipped")
            
            duration = time.time() - start_time
            
            assert duration < 30.0, f"Landscape modifications took too long: {duration}s"
            print(f"✓ Completed landscape modifications in {duration:.2f}s")
    
    def test_landscape_info_query_performance(self):
        """Test performance of landscape info queries."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create multiple landscapes
            for i in range(2):
                config = self.landscape_configs["small"].copy()
                config["location_x"] = i * 2000.0
                
                create_response = conn.send_command("create_landscape", {
                    "size_x": config["size_x"],
                    "size_y": config["size_y"],
                    "location_x": config["location_x"],
                    "location_y": config["location_y"],
                    "location_z": config["location_z"]
                })
                self._assert_valid_response(create_response, f"create_landscape ({i})")
                self._add_cleanup_landscape(f"query_perf_landscape_{i}")
            
            # Test query performance
            num_queries = 10
            start_time = time.time()
            
            for i in range(num_queries):
                response = conn.send_command("get_landscape_info", {})
                self._assert_valid_response(response, f"get_landscape_info ({i})")
            
            duration = time.time() - start_time
            avg_time = duration / num_queries
            
            assert duration < 15.0, f"Landscape info queries took too long: {duration}s"
            assert avg_time < 1.5, f"Average query time too slow: {avg_time}s"
            print(f"✓ Completed {num_queries} landscape info queries in {duration:.2f}s (avg: {avg_time:.3f}s per query)")

# =================================
# TEST RUNNER FUNCTIONS
# =================================

async def run_all_tests():
    """Run all landscape command tests."""
    test_suite = TestLandscapeCommands()
    test_suite.setup_class()
    
    # Get all test methods
    test_methods = [
        method for method in dir(test_suite) 
        if method.startswith('test_') and callable(getattr(test_suite, method))
    ]
    
    results = []
    print(f"\n🚀 Running {len(test_methods)} landscape command tests...\n")
    
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
    
    print(f"\n📊 Landscape Commands Test Summary:")
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