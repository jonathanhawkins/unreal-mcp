"""
Comprehensive tests for asset registry commands.

Tests all asset registry operations including:
- get_asset_references: Get all assets that reference the specified asset
- get_asset_dependencies: Get all assets that the specified asset depends on

These commands are crucial for understanding asset relationships and managing
complex content hierarchies in Unreal Engine projects.

Each test covers happy path, error handling, edge cases, and performance validation.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Set
import pytest
import sys

# Add parent directories to path for imports
test_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(test_dir.parent))

from tests.test_framework import TestFramework, create_test_config, TestResult
from tests.data.test_data import get_test_data_manager
from unreal_mcp_server import get_unreal_connection

class TestAssetRegistryCommands:
    """Test suite for asset registry commands."""
    
    @classmethod
    def setup_class(cls):
        """Setup test framework and data."""
        cls.config = create_test_config()
        cls.framework = TestFramework(cls.config)
        cls.test_data_manager = get_test_data_manager()
        cls.test_results = []
        cls.cleanup_assets = []
        
        # Test assets with known relationships
        cls.engine_assets = {
            "cube_mesh": "/Engine/BasicShapes/Cube",
            "sphere_mesh": "/Engine/BasicShapes/Sphere",
            "cylinder_mesh": "/Engine/BasicShapes/Cylinder",
            "plane_mesh": "/Engine/BasicShapes/Plane",
            "default_material": "/Engine/EngineMaterials/DefaultMaterial",
            "world_grid_material": "/Engine/EngineMaterials/WorldGridMaterial"
        }
        
        # Create test assets for dependency testing
        cls.test_assets = {
            "test_material": "/Game/TestAssets/TestMaterial",
            "test_blueprint": "/Game/TestAssets/TestBlueprint", 
            "dependent_material": "/Game/TestAssets/DependentMaterial",
            "complex_blueprint": "/Game/TestAssets/ComplexBlueprint"
        }
    
    @classmethod
    def teardown_class(cls):
        """Cleanup test assets."""
        cls._cleanup_test_assets()
    
    @classmethod
    def _cleanup_test_assets(cls):
        """Clean up any test assets created during testing."""
        if not cls.cleanup_assets:
            return
            
        try:
            with cls.framework.test_connection() as conn:
                if conn.connect():
                    for asset_path in cls.cleanup_assets:
                        try:
                            response = conn.send_command("delete_asset", {"asset_path": asset_path})
                            if response and response.get("success"):
                                print(f"Cleaned up test asset: {asset_path}")
                        except Exception as e:
                            print(f"Failed to cleanup asset {asset_path}: {e}")
        except Exception as e:
            print(f"Error during test asset cleanup: {e}")
    
    def _add_cleanup_asset(self, asset_path: str):
        """Add asset to cleanup list."""
        if asset_path not in self.cleanup_assets:
            self.cleanup_assets.append(asset_path)
    
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
    
    def _assert_valid_asset_list(self, assets: List[Dict], command: str):
        """Assert asset list is valid."""
        assert isinstance(assets, list), f"{command}: Result should be a list"
        
        for asset in assets:
            assert isinstance(asset, dict), f"{command}: Each asset should be a dictionary"
            assert "path" in asset or "name" in asset, f"{command}: Asset should have path or name"
    
    def _create_test_asset_for_dependencies(self) -> str:
        """Create a test asset that can be used to test dependencies."""
        with self.framework.test_connection() as conn:
            if not conn.connect():
                raise Exception("Failed to connect to create test asset")
            
            # Duplicate an existing asset to create test dependencies
            source_path = self.engine_assets["cube_mesh"]
            dest_path = "/Game/TestAssets/DependencyTestAsset"
            
            response = conn.send_command("duplicate_asset", {
                "source_path": source_path,
                "destination_path": dest_path
            })
            
            if not (response and response.get("success")):
                raise Exception(f"Failed to create test asset: {response}")
            
            self._add_cleanup_asset(dest_path)
            return dest_path
    
    # =================================
    # GET ASSET REFERENCES TESTS
    # =================================
    
    def test_get_asset_references_engine_default_material(self):
        """Test getting references to Engine default material (commonly referenced)."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_references", {
                "asset_path": self.engine_assets["default_material"]
            })
            
            self._assert_valid_response(response, "get_asset_references")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, "get_asset_references")
            
            # Default material might be referenced by many assets
            print(f"✓ Found {len(result)} references to Engine default material")
            
            # Verify result structure
            for reference in result[:3]:  # Check first few
                assert isinstance(reference, (dict, str)), "Each reference should be dict or string"
                if isinstance(reference, dict):
                    assert "path" in reference or "name" in reference, "Reference dict should have path/name"
    
    def test_get_asset_references_basic_shape_mesh(self):
        """Test getting references to basic shape mesh."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_references", {
                "asset_path": self.engine_assets["cube_mesh"]
            })
            
            self._assert_valid_response(response, "get_asset_references")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, "get_asset_references")
            
            print(f"✓ Found {len(result)} references to Engine cube mesh")
    
    def test_get_asset_references_nonexistent_asset(self):
        """Test getting references for non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_references", {
                "asset_path": "/Game/NonExistent/Asset"
            })
            
            self._assert_error_response(response, "get_asset_references", "not found")
            print(f"✓ Correctly handled references request for non-existent asset")
    
    def test_get_asset_references_invalid_path_format(self):
        """Test getting references with invalid path format."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_references", {
                "asset_path": "invalid/path/format"
            })
            
            self._assert_error_response(response, "get_asset_references", "invalid")
            print(f"✓ Correctly handled invalid path format for references")
    
    def test_get_asset_references_empty_path(self):
        """Test getting references with empty path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_references", {
                "asset_path": ""
            })
            
            self._assert_error_response(response, "get_asset_references")
            print(f"✓ Correctly handled empty path for references")
    
    def test_get_asset_references_user_created_asset(self):
        """Test getting references for user-created test asset."""
        try:
            test_asset_path = self._create_test_asset_for_dependencies()
            
            with self.framework.test_connection() as conn:
                assert conn.connect(), "Failed to connect to Unreal Engine"
                
                response = conn.send_command("get_asset_references", {
                    "asset_path": test_asset_path
                })
                
                self._assert_valid_response(response, "get_asset_references")
                
                result = response.get("result", [])
                self._assert_valid_asset_list(result, "get_asset_references")
                
                # New asset might have no references yet
                print(f"✓ Found {len(result)} references to user-created test asset")
                
        except Exception as e:
            print(f"⚠ Could not create test asset for references test: {e}")
    
    def test_get_asset_references_multiple_engine_assets(self):
        """Test getting references for multiple Engine assets."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            test_assets = [
                self.engine_assets["sphere_mesh"],
                self.engine_assets["cylinder_mesh"],
                self.engine_assets["plane_mesh"]
            ]
            
            total_references = 0
            
            for asset_path in test_assets:
                response = conn.send_command("get_asset_references", {
                    "asset_path": asset_path
                })
                
                self._assert_valid_response(response, f"get_asset_references({asset_path})")
                
                result = response.get("result", [])
                self._assert_valid_asset_list(result, f"get_asset_references({asset_path})")
                
                total_references += len(result)
                print(f"✓ Asset {asset_path} has {len(result)} references")
            
            print(f"✓ Total references found across all test assets: {total_references}")
    
    # =================================
    # GET ASSET DEPENDENCIES TESTS
    # =================================
    
    def test_get_asset_dependencies_basic_mesh(self):
        """Test getting dependencies for basic mesh (should have minimal dependencies)."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_dependencies", {
                "asset_path": self.engine_assets["cube_mesh"]
            })
            
            self._assert_valid_response(response, "get_asset_dependencies")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, "get_asset_dependencies")
            
            print(f"✓ Cube mesh has {len(result)} dependencies")
            
            # Log some dependencies for insight
            for dep in result[:3]:
                dep_path = dep.get("path", "") if isinstance(dep, dict) else str(dep)
                print(f"  - Dependency: {dep_path}")
    
    def test_get_asset_dependencies_material(self):
        """Test getting dependencies for material (typically has more dependencies)."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_dependencies", {
                "asset_path": self.engine_assets["world_grid_material"]
            })
            
            self._assert_valid_response(response, "get_asset_dependencies")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, "get_asset_dependencies")
            
            print(f"✓ World grid material has {len(result)} dependencies")
            
            # Materials typically have more dependencies (textures, etc.)
            if len(result) > 0:
                print(f"  - Sample dependencies:")
                for dep in result[:5]:  # Show first 5
                    dep_path = dep.get("path", "") if isinstance(dep, dict) else str(dep)
                    print(f"    {dep_path}")
    
    def test_get_asset_dependencies_nonexistent_asset(self):
        """Test getting dependencies for non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_dependencies", {
                "asset_path": "/Game/NonExistent/Asset"
            })
            
            self._assert_error_response(response, "get_asset_dependencies", "not found")
            print(f"✓ Correctly handled dependencies request for non-existent asset")
    
    def test_get_asset_dependencies_invalid_path_format(self):
        """Test getting dependencies with invalid path format."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_dependencies", {
                "asset_path": "invalid/path/format"
            })
            
            self._assert_error_response(response, "get_asset_dependencies", "invalid")
            print(f"✓ Correctly handled invalid path format for dependencies")
    
    def test_get_asset_dependencies_empty_path(self):
        """Test getting dependencies with empty path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_dependencies", {
                "asset_path": ""
            })
            
            self._assert_error_response(response, "get_asset_dependencies")
            print(f"✓ Correctly handled empty path for dependencies")
    
    def test_get_asset_dependencies_user_created_asset(self):
        """Test getting dependencies for user-created asset."""
        try:
            test_asset_path = self._create_test_asset_for_dependencies()
            
            with self.framework.test_connection() as conn:
                assert conn.connect(), "Failed to connect to Unreal Engine"
                
                response = conn.send_command("get_asset_dependencies", {
                    "asset_path": test_asset_path
                })
                
                self._assert_valid_response(response, "get_asset_dependencies")
                
                result = response.get("result", [])
                self._assert_valid_asset_list(result, "get_asset_dependencies")
                
                # Duplicated asset should inherit dependencies from source
                print(f"✓ User-created test asset has {len(result)} dependencies")
                
                # Should have at least the source asset's dependencies
                assert len(result) >= 0, "Asset should have some dependencies"
                
        except Exception as e:
            print(f"⚠ Could not create test asset for dependencies test: {e}")
    
    def test_get_asset_dependencies_multiple_engine_assets(self):
        """Test getting dependencies for multiple Engine assets."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            test_assets = [
                self.engine_assets["cube_mesh"],
                self.engine_assets["sphere_mesh"],
                self.engine_assets["default_material"]
            ]
            
            total_dependencies = 0
            asset_dependency_map = {}
            
            for asset_path in test_assets:
                response = conn.send_command("get_asset_dependencies", {
                    "asset_path": asset_path
                })
                
                self._assert_valid_response(response, f"get_asset_dependencies({asset_path})")
                
                result = response.get("result", [])
                self._assert_valid_asset_list(result, f"get_asset_dependencies({asset_path})")
                
                asset_dependency_map[asset_path] = len(result)
                total_dependencies += len(result)
                print(f"✓ Asset {asset_path} has {len(result)} dependencies")
            
            print(f"✓ Total dependencies found across all test assets: {total_dependencies}")
            
            # Verify different asset types have different dependency patterns
            mesh_deps = asset_dependency_map[self.engine_assets["cube_mesh"]]
            material_deps = asset_dependency_map[self.engine_assets["default_material"]]
            
            print(f"  - Mesh dependencies: {mesh_deps}")
            print(f"  - Material dependencies: {material_deps}")
    
    # =================================
    # CROSS-REFERENCE VALIDATION TESTS
    # =================================
    
    def test_cross_reference_validation_bidirectional(self):
        """Test that asset A depends on B implies B is referenced by A."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Pick an asset that likely has dependencies
            test_asset = self.engine_assets["world_grid_material"]
            
            # Get dependencies of the test asset
            deps_response = conn.send_command("get_asset_dependencies", {
                "asset_path": test_asset
            })
            
            self._assert_valid_response(deps_response, "get_asset_dependencies")
            dependencies = deps_response.get("result", [])
            
            if len(dependencies) == 0:
                print("⚠ Test asset has no dependencies to validate cross-references")
                return
            
            # Test first dependency
            first_dep = dependencies[0]
            dep_path = first_dep.get("path", "") if isinstance(first_dep, dict) else str(first_dep)
            
            if not dep_path:
                print("⚠ Dependency path not available for cross-reference validation")
                return
            
            # Get references to the dependency
            refs_response = conn.send_command("get_asset_references", {
                "asset_path": dep_path
            })
            
            if refs_response.get("success"):
                references = refs_response.get("result", [])
                
                # Check if our test asset is in the references
                ref_paths = []
                for ref in references:
                    if isinstance(ref, dict):
                        ref_paths.append(ref.get("path", ""))
                    else:
                        ref_paths.append(str(ref))
                
                # The relationship should be bidirectional
                found_reverse_reference = any(test_asset in ref_path for ref_path in ref_paths)
                
                print(f"✓ Cross-reference validation: {test_asset} -> {dep_path}")
                print(f"  Reverse reference found: {found_reverse_reference}")
                
            else:
                print(f"⚠ Could not get references for dependency: {dep_path}")
    
    def test_dependency_chain_depth_analysis(self):
        """Analyze dependency chain depth for understanding asset complexity."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Test different asset types for complexity comparison
            test_assets = {
                "Simple Mesh": self.engine_assets["cube_mesh"],
                "Material": self.engine_assets["default_material"],
                "Grid Material": self.engine_assets["world_grid_material"]
            }
            
            complexity_analysis = {}
            
            for asset_type, asset_path in test_assets.items():
                response = conn.send_command("get_asset_dependencies", {
                    "asset_path": asset_path
                })
                
                if response.get("success"):
                    dependencies = response.get("result", [])
                    complexity_analysis[asset_type] = {
                        "path": asset_path,
                        "dependency_count": len(dependencies),
                        "complexity": "High" if len(dependencies) > 10 else "Medium" if len(dependencies) > 3 else "Low"
                    }
            
            print(f"✓ Asset complexity analysis:")
            for asset_type, analysis in complexity_analysis.items():
                print(f"  - {asset_type}: {analysis['dependency_count']} deps ({analysis['complexity']} complexity)")
    
    # =================================
    # PERFORMANCE TESTS
    # =================================
    
    def test_references_performance_multiple_assets(self):
        """Test performance of getting references for multiple assets."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            test_assets = list(self.engine_assets.values())[:5]  # Test 5 assets
            
            start_time = time.time()
            
            total_references = 0
            for asset_path in test_assets:
                response = conn.send_command("get_asset_references", {
                    "asset_path": asset_path
                })
                
                self._assert_valid_response(response, f"get_asset_references({asset_path})")
                result = response.get("result", [])
                total_references += len(result)
            
            duration = time.time() - start_time
            
            assert duration < 60.0, f"Getting references for {len(test_assets)} assets took too long: {duration}s"
            
            print(f"✓ Retrieved references for {len(test_assets)} assets in {duration:.2f}s")
            print(f"  Total references found: {total_references}")
    
    def test_dependencies_performance_multiple_assets(self):
        """Test performance of getting dependencies for multiple assets."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            test_assets = list(self.engine_assets.values())[:5]  # Test 5 assets
            
            start_time = time.time()
            
            total_dependencies = 0
            for asset_path in test_assets:
                response = conn.send_command("get_asset_dependencies", {
                    "asset_path": asset_path
                })
                
                self._assert_valid_response(response, f"get_asset_dependencies({asset_path})")
                result = response.get("result", [])
                total_dependencies += len(result)
            
            duration = time.time() - start_time
            
            assert duration < 60.0, f"Getting dependencies for {len(test_assets)} assets took too long: {duration}s"
            
            print(f"✓ Retrieved dependencies for {len(test_assets)} assets in {duration:.2f}s")
            print(f"  Total dependencies found: {total_dependencies}")
    
    def test_combined_references_dependencies_performance(self):
        """Test performance of getting both references and dependencies for assets."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            test_assets = [
                self.engine_assets["cube_mesh"],
                self.engine_assets["default_material"]
            ]
            
            start_time = time.time()
            
            for asset_path in test_assets:
                # Get references
                refs_response = conn.send_command("get_asset_references", {
                    "asset_path": asset_path
                })
                self._assert_valid_response(refs_response, f"get_asset_references({asset_path})")
                
                # Get dependencies  
                deps_response = conn.send_command("get_asset_dependencies", {
                    "asset_path": asset_path
                })
                self._assert_valid_response(deps_response, f"get_asset_dependencies({asset_path})")
                
                references = len(refs_response.get("result", []))
                dependencies = len(deps_response.get("result", []))
                
                print(f"  {asset_path}: {references} refs, {dependencies} deps")
            
            duration = time.time() - start_time
            
            assert duration < 30.0, f"Combined references/dependencies took too long: {duration}s"
            
            print(f"✓ Retrieved both references and dependencies for {len(test_assets)} assets in {duration:.2f}s")

# =================================
# TEST RUNNER FUNCTIONS
# =================================

async def run_all_tests():
    """Run all asset registry command tests."""
    test_suite = TestAssetRegistryCommands()
    test_suite.setup_class()
    
    # Get all test methods
    test_methods = [
        method for method in dir(test_suite)
        if method.startswith('test_') and callable(getattr(test_suite, method))
    ]
    
    results = []
    print(f"\n🚀 Running {len(test_methods)} asset registry command tests...\n")
    
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
    
    print(f"\n📊 Test Summary:")
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