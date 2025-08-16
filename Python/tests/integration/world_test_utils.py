"""
Utility functions for World/Level Management testing.

Provides common utilities for testing world and level operations including:
- Level creation and cleanup helpers
- Landscape testing utilities  
- World state validation
- Performance testing helpers
- Mock data generators
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import sys

# Add parent directories to path for imports
test_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(test_dir.parent))

from tests.test_framework import TestFramework, TestResult
from tests.data.test_data import get_test_data_manager, LevelTestData
from unreal_mcp_server import get_unreal_connection

@dataclass
class LevelTestContext:
    """Context information for level testing."""
    level_name: str
    level_path: str
    created: bool = False
    loaded: bool = False
    saved: bool = False
    has_streaming_levels: bool = False
    streaming_level_count: int = 0
    actor_count: int = 0
    landscape_count: int = 0
    cleanup_required: bool = True

@dataclass 
class LandscapeTestContext:
    """Context information for landscape testing."""
    size_x: int
    size_y: int
    location: Tuple[float, float, float]
    sections_per_component: int
    quads_per_section: int
    created: bool = False
    modified: bool = False
    painted_layers: List[str] = None
    cleanup_required: bool = True
    
    def __post_init__(self):
        if self.painted_layers is None:
            self.painted_layers = []

@dataclass
class WorldTestState:
    """Snapshot of world state for testing."""
    current_level_name: Optional[str] = None
    current_level_path: Optional[str] = None
    total_actors: int = 0
    total_landscapes: int = 0
    streaming_levels: List[str] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.streaming_levels is None:
            self.streaming_levels = []
        if self.timestamp == 0.0:
            self.timestamp = time.time()

class WorldTestUtils:
    """Utility class for world and level testing operations."""
    
    def __init__(self, framework: TestFramework):
        self.framework = framework
        self.test_data_manager = get_test_data_manager()
        self.level_contexts: List[LevelTestContext] = []
        self.landscape_contexts: List[LandscapeTestContext] = []
        self.world_snapshots: List[WorldTestState] = []
    
    # =================================
    # LEVEL UTILITIES
    # =================================
    
    def create_test_level(self, level_name: str, template: str = "Default") -> LevelTestContext:
        """Create a test level and return its context."""
        level_path = f"/Game/{level_name}"
        context = LevelTestContext(
            level_name=level_name,
            level_path=level_path
        )
        
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("create_level", {
                    "level_name": level_name,
                    "template": template
                })
                
                if response and response.get("success"):
                    context.created = True
                    self.level_contexts.append(context)
                    print(f"Created test level: {level_name}")
                else:
                    print(f"Failed to create test level: {level_name}")
        
        return context
    
    def load_test_level(self, context: LevelTestContext) -> bool:
        """Load a test level."""
        if not context.created:
            return False
        
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("load_level", {
                    "level_path": context.level_path
                })
                
                if response and response.get("success"):
                    context.loaded = True
                    print(f"Loaded test level: {context.level_name}")
                    return True
                else:
                    print(f"Failed to load test level: {context.level_name}")
        
        return False
    
    def save_test_level(self, context: LevelTestContext) -> bool:
        """Save a test level."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("save_level", {})
                
                if response and response.get("success"):
                    context.saved = True
                    print(f"Saved test level: {context.level_name}")
                    return True
                else:
                    print(f"Failed to save test level: {context.level_name}")
        
        return False
    
    def add_streaming_level(self, main_context: LevelTestContext, streaming_level_name: str) -> bool:
        """Add a streaming level to the main level."""
        # Create the streaming level first
        streaming_context = self.create_test_level(streaming_level_name)
        if not streaming_context.created:
            return False
        
        # Add it as a streaming level
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("create_streaming_level", {
                    "level_path": streaming_context.level_path
                })
                
                if response and response.get("success"):
                    main_context.has_streaming_levels = True
                    main_context.streaming_level_count += 1
                    print(f"Added streaming level {streaming_level_name} to {main_context.level_name}")
                    return True
                else:
                    print(f"Failed to add streaming level: {streaming_level_name}")
        
        return False
    
    def verify_level_exists(self, level_path: str) -> bool:
        """Verify that a level exists and can be queried."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                # Try to get current level info to see if level operations work
                response = conn.send_command("get_current_level_info", {})
                return response and response.get("success")
        return False
    
    def get_level_actor_count(self) -> int:
        """Get the number of actors in the current level."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("get_actors_in_level", {})
                if response and response.get("success"):
                    actors = response.get("result", [])
                    return len(actors) if isinstance(actors, list) else 0
        return 0
    
    def cleanup_level_contexts(self):
        """Clean up all created test levels."""
        for context in self.level_contexts:
            if context.cleanup_required:
                print(f"Would cleanup level: {context.level_name}")
        self.level_contexts.clear()
    
    # =================================
    # LANDSCAPE UTILITIES
    # =================================
    
    def create_test_landscape(self, 
                            size_x: int = 127, 
                            size_y: int = 127,
                            location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                            sections_per_component: int = 1,
                            quads_per_section: int = 63) -> LandscapeTestContext:
        """Create a test landscape and return its context."""
        context = LandscapeTestContext(
            size_x=size_x,
            size_y=size_y,
            location=location,
            sections_per_component=sections_per_component,
            quads_per_section=quads_per_section
        )
        
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("create_landscape", {
                    "size_x": size_x,
                    "size_y": size_y,
                    "sections_per_component": sections_per_component,
                    "quads_per_section": quads_per_section,
                    "location_x": location[0],
                    "location_y": location[1],
                    "location_z": location[2]
                })
                
                if response and response.get("success"):
                    context.created = True
                    self.landscape_contexts.append(context)
                    print(f"Created test landscape: {size_x}x{size_y} at {location}")
                else:
                    print(f"Failed to create test landscape: {size_x}x{size_y}")
        
        return context
    
    def modify_test_landscape(self, context: LandscapeTestContext, modification_type: str = "sculpt") -> bool:
        """Modify a test landscape."""
        if not context.created:
            return False
        
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("modify_landscape", {
                    "modification_type": modification_type
                })
                
                if response and response.get("success"):
                    context.modified = True
                    print(f"Modified landscape with {modification_type}")
                    return True
                else:
                    print(f"Failed to modify landscape with {modification_type}")
        
        return False
    
    def paint_landscape_layer(self, context: LandscapeTestContext, layer_name: str) -> bool:
        """Paint a layer on a test landscape."""
        if not context.created:
            return False
        
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("paint_landscape_layer", {
                    "layer_name": layer_name
                })
                
                if response and response.get("success"):
                    if layer_name not in context.painted_layers:
                        context.painted_layers.append(layer_name)
                    print(f"Painted layer {layer_name} on landscape")
                    return True
                else:
                    print(f"Failed to paint layer {layer_name}")
        
        return False
    
    def get_landscape_count(self) -> int:
        """Get the number of landscapes in the current level."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("get_landscape_info", {})
                if response and response.get("success"):
                    landscapes = response.get("result", [])
                    if isinstance(landscapes, dict) and "landscapes" in landscapes:
                        landscapes = landscapes["landscapes"]
                    return len(landscapes) if isinstance(landscapes, list) else 0
        return 0
    
    def verify_landscape_properties(self, context: LandscapeTestContext) -> Dict[str, bool]:
        """Verify landscape properties match expected values."""
        results = {
            "exists": False,
            "correct_size": False,
            "correct_location": False
        }
        
        with self.framework.test_connection() as conn:
            if conn.connect():
                response = conn.send_command("get_landscape_info", {})
                if response and response.get("success"):
                    landscapes = response.get("result", [])
                    if isinstance(landscapes, dict) and "landscapes" in landscapes:
                        landscapes = landscapes["landscapes"]
                    
                    for landscape in landscapes:
                        if isinstance(landscape, dict):
                            results["exists"] = True
                            
                            # Check size
                            size_x = landscape.get("size_x") or landscape.get("width")
                            size_y = landscape.get("size_y") or landscape.get("height")
                            if size_x == context.size_x and size_y == context.size_y:
                                results["correct_size"] = True
                            
                            # Check location (with tolerance)
                            location = landscape.get("location") or landscape.get("position")
                            if location:
                                if isinstance(location, (list, tuple)) and len(location) >= 3:
                                    tolerance = 10.0
                                    if (abs(location[0] - context.location[0]) < tolerance and
                                        abs(location[1] - context.location[1]) < tolerance and
                                        abs(location[2] - context.location[2]) < tolerance):
                                        results["correct_location"] = True
                            break
        
        return results
    
    def cleanup_landscape_contexts(self):
        """Clean up all created test landscapes."""
        for context in self.landscape_contexts:
            if context.cleanup_required:
                print(f"Would cleanup landscape: {context.size_x}x{context.size_y}")
        self.landscape_contexts.clear()
    
    # =================================
    # WORLD STATE UTILITIES
    # =================================
    
    def capture_world_state(self) -> WorldTestState:
        """Capture a snapshot of the current world state."""
        state = WorldTestState()
        
        with self.framework.test_connection() as conn:
            if conn.connect():
                # Get current level info
                level_response = conn.send_command("get_current_level_info", {})
                if level_response and level_response.get("success"):
                    level_info = level_response.get("result", {})
                    state.current_level_name = level_info.get("level_name") or level_info.get("name")
                    state.current_level_path = level_info.get("level_path") or level_info.get("path")
                
                # Get actor count
                actor_response = conn.send_command("get_actors_in_level", {})
                if actor_response and actor_response.get("success"):
                    actors = actor_response.get("result", [])
                    state.total_actors = len(actors) if isinstance(actors, list) else 0
                
                # Get landscape count
                landscape_response = conn.send_command("get_landscape_info", {})
                if landscape_response and landscape_response.get("success"):
                    landscapes = landscape_response.get("result", [])
                    if isinstance(landscapes, dict) and "landscapes" in landscapes:
                        landscapes = landscapes["landscapes"]
                    state.total_landscapes = len(landscapes) if isinstance(landscapes, list) else 0
        
        self.world_snapshots.append(state)
        return state
    
    def compare_world_states(self, state1: WorldTestState, state2: WorldTestState) -> Dict[str, Any]:
        """Compare two world states and return the differences."""
        comparison = {
            "level_changed": state1.current_level_name != state2.current_level_name,
            "actor_count_changed": state1.total_actors != state2.total_actors,
            "landscape_count_changed": state1.total_landscapes != state2.total_landscapes,
            "time_elapsed": state2.timestamp - state1.timestamp,
            "details": {
                "level": {
                    "before": state1.current_level_name,
                    "after": state2.current_level_name
                },
                "actors": {
                    "before": state1.total_actors,
                    "after": state2.total_actors,
                    "change": state2.total_actors - state1.total_actors
                },
                "landscapes": {
                    "before": state1.total_landscapes,
                    "after": state2.total_landscapes,
                    "change": state2.total_landscapes - state1.total_landscapes
                }
            }
        }
        
        return comparison
    
    def wait_for_world_state_change(self, initial_state: WorldTestState, 
                                  timeout: float = 10.0,
                                  check_interval: float = 0.5) -> Optional[WorldTestState]:
        """Wait for world state to change from initial state."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_state = self.capture_world_state()
            comparison = self.compare_world_states(initial_state, current_state)
            
            if (comparison["level_changed"] or 
                comparison["actor_count_changed"] or 
                comparison["landscape_count_changed"]):
                return current_state
            
            time.sleep(check_interval)
        
        return None
    
    # =================================
    # PERFORMANCE TESTING UTILITIES
    # =================================
    
    def time_level_operation(self, operation: str, params: Dict[str, Any]) -> Tuple[bool, float, Dict[str, Any]]:
        """Time a level operation and return success, duration, and response."""
        with self.framework.test_connection() as conn:
            if conn.connect():
                start_time = time.time()
                response = conn.send_command(operation, params)
                duration = time.time() - start_time
                
                success = response and response.get("success")
                return success, duration, response
        
        return False, 0.0, {}
    
    def benchmark_level_operations(self, operations: List[Tuple[str, Dict[str, Any]]], 
                                 iterations: int = 1) -> Dict[str, Dict[str, float]]:
        """Benchmark multiple level operations."""
        results = {}
        
        for operation, params in operations:
            operation_results = {
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "success_rate": 0.0
            }
            
            successful = 0
            times = []
            
            for i in range(iterations):
                success, duration, _ = self.time_level_operation(operation, params)
                if success:
                    successful += 1
                times.append(duration)
                
                operation_results["total_time"] += duration
                operation_results["min_time"] = min(operation_results["min_time"], duration)
                operation_results["max_time"] = max(operation_results["max_time"], duration)
            
            operation_results["avg_time"] = operation_results["total_time"] / iterations
            operation_results["success_rate"] = successful / iterations
            results[operation] = operation_results
        
        return results
    
    def stress_test_level_operations(self, operation: str, params: Dict[str, Any], 
                                   max_operations: int = 10, 
                                   time_limit: float = 30.0) -> Dict[str, Any]:
        """Stress test a level operation."""
        results = {
            "operations_completed": 0,
            "operations_successful": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "errors": []
        }
        
        start_time = time.time()
        
        for i in range(max_operations):
            if time.time() - start_time > time_limit:
                break
            
            success, duration, response = self.time_level_operation(operation, params)
            results["operations_completed"] += 1
            results["total_time"] += duration
            
            if success:
                results["operations_successful"] += 1
            else:
                error_msg = response.get("error", "Unknown error") if response else "No response"
                results["errors"].append(f"Op {i}: {error_msg}")
        
        if results["operations_completed"] > 0:
            results["avg_time"] = results["total_time"] / results["operations_completed"]
            results["success_rate"] = results["operations_successful"] / results["operations_completed"]
        
        return results
    
    # =================================
    # MOCK DATA UTILITIES  
    # =================================
    
    def generate_test_level_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock level data for testing."""
        levels = []
        for i in range(count):
            levels.append({
                "level_name": f"MockLevel_{i}",
                "level_path": f"/Game/MockLevels/MockLevel_{i}",
                "template": "Default" if i % 2 == 0 else "Empty",
                "expected_actors": ["WorldSettings", "PostProcessVolume"] if i % 2 == 0 else ["WorldSettings"]
            })
        return levels
    
    def generate_test_landscape_data(self, count: int = 3) -> List[Dict[str, Any]]:
        """Generate mock landscape data for testing."""
        landscapes = []
        sizes = [(63, 63), (127, 127), (255, 255)]
        
        for i in range(count):
            size = sizes[i % len(sizes)]
            landscapes.append({
                "size_x": size[0],
                "size_y": size[1],
                "sections_per_component": 1 + (i % 2),
                "quads_per_section": 31 + (i % 2) * 32,
                "location": [i * 2000.0, 0.0, 0.0],
                "expected_layers": ["Grass", "Dirt", "Rock"]
            })
        return landscapes
    
    def generate_mock_world_responses(self) -> Dict[str, Dict[str, Any]]:
        """Generate mock responses for world operations."""
        return {
            "create_level": {
                "success": True,
                "result": "Level created successfully",
                "level_name": "TestLevel",
                "level_path": "/Game/TestLevel"
            },
            "load_level": {
                "success": True,
                "result": "Level loaded successfully",
                "level_path": "/Game/TestLevel",
                "load_time": 2.5
            },
            "save_level": {
                "success": True,
                "result": "Level saved successfully",
                "save_time": 1.2
            },
            "get_current_level_info": {
                "success": True,
                "result": {
                    "level_name": "TestLevel",
                    "level_path": "/Game/TestLevel",
                    "world_name": "TestWorld",
                    "is_persistent": True,
                    "is_visible": True,
                    "actors": [
                        {"name": "WorldSettings", "type": "WorldSettings"},
                        {"name": "PostProcessVolume", "type": "PostProcessVolume"}
                    ],
                    "streaming_levels": [],
                    "lighting_scenario": "Stationary"
                }
            },
            "create_landscape": {
                "success": True,
                "result": "Landscape created successfully",
                "landscape_id": "Landscape_1",
                "size": [127, 127],
                "location": [0, 0, 0]
            },
            "get_landscape_info": {
                "success": True,
                "result": {
                    "landscapes": [
                        {
                            "size_x": 127,
                            "size_y": 127,
                            "location": [0, 0, 0],
                            "sections_per_component": 1,
                            "quads_per_section": 63,
                            "components": 4
                        }
                    ]
                }
            }
        }
    
    # =================================
    # CLEANUP UTILITIES
    # =================================
    
    def cleanup_all_contexts(self):
        """Clean up all test contexts and snapshots."""
        self.cleanup_level_contexts()
        self.cleanup_landscape_contexts()
        self.world_snapshots.clear()
        print("Cleaned up all world test contexts")
    
    def get_cleanup_summary(self) -> Dict[str, int]:
        """Get summary of items that need cleanup."""
        return {
            "levels": len(self.level_contexts),
            "landscapes": len(self.landscape_contexts),
            "snapshots": len(self.world_snapshots)
        }

# =================================
# CONVENIENCE FUNCTIONS
# =================================

def create_world_test_utils(framework: TestFramework) -> WorldTestUtils:
    """Create a WorldTestUtils instance with the given framework."""
    return WorldTestUtils(framework)

def quick_level_test(framework: TestFramework, level_name: str) -> Tuple[bool, LevelTestContext]:
    """Quick test to create, load, and verify a level."""
    utils = create_world_test_utils(framework)
    
    # Create level
    context = utils.create_test_level(level_name)
    if not context.created:
        return False, context
    
    # Save level
    if not utils.save_test_level(context):
        return False, context
    
    # Load level
    if not utils.load_test_level(context):
        return False, context
    
    # Verify existence
    if not utils.verify_level_exists(context.level_path):
        return False, context
    
    return True, context

def quick_landscape_test(framework: TestFramework) -> Tuple[bool, LandscapeTestContext]:
    """Quick test to create and verify a landscape."""
    utils = create_world_test_utils(framework)
    
    # Create landscape
    context = utils.create_test_landscape(127, 127, (0.0, 0.0, 0.0))
    if not context.created:
        return False, context
    
    # Verify properties
    properties = utils.verify_landscape_properties(context)
    if not properties["exists"]:
        return False, context
    
    return True, context

def measure_world_operation_performance(framework: TestFramework, 
                                      operation: str, 
                                      params: Dict[str, Any],
                                      iterations: int = 5) -> Dict[str, float]:
    """Measure performance of a world operation."""
    utils = create_world_test_utils(framework)
    
    results = utils.benchmark_level_operations([(operation, params)], iterations)
    return results.get(operation, {})

def compare_world_states_over_time(framework: TestFramework, 
                                 duration: float = 5.0,
                                 interval: float = 1.0) -> List[WorldTestState]:
    """Capture world states over time for comparison."""
    utils = create_world_test_utils(framework)
    states = []
    
    start_time = time.time()
    while time.time() - start_time < duration:
        state = utils.capture_world_state()
        states.append(state)
        time.sleep(interval)
    
    return states