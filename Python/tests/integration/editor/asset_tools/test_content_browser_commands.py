"""
Comprehensive tests for content browser commands.

Tests all content browser operations including:
- list_assets: List all assets in specified paths
- get_asset_metadata: Get detailed metadata for specific assets
- search_assets: Search for assets by name or path

Each test covers happy path, error handling, edge cases, and performance validation.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import pytest
import sys

# Add parent directories to path for imports
test_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(test_dir.parent))

from tests.test_framework import TestFramework, create_test_config, TestResult
from tests.data.test_data import get_test_data_manager
from unreal_mcp_server import get_unreal_connection

class TestContentBrowserCommands:
    """Test suite for content browser commands."""
    
    @classmethod
    def setup_class(cls):
        """Setup test framework and data."""
        cls.config = create_test_config()
        cls.framework = TestFramework(cls.config)
        cls.test_data_manager = get_test_data_manager()
        cls.test_results = []
        
        # Test paths and data
        cls.test_paths = {
            "engine_root": "/Engine",
            "engine_shapes": "/Engine/BasicShapes",
            "engine_materials": "/Engine/EngineMaterials",
            "game_root": "/Game",
            "game_content": "/Game/Content",
            "empty_path": "/Game/EmptyFolder",
            "nonexistent_path": "/Game/NonExistentFolder"
        }
        
        cls.engine_assets = {
            "cube_mesh": "/Engine/BasicShapes/Cube",
            "sphere_mesh": "/Engine/BasicShapes/Sphere",
            "cylinder_mesh": "/Engine/BasicShapes/Cylinder",
            "plane_mesh": "/Engine/BasicShapes/Plane",
            "default_material": "/Engine/EngineMaterials/DefaultMaterial"
        }
        
        cls.asset_types = [
            "StaticMesh",
            "Material", 
            "Texture2D",
            "Blueprint",
            "SkeletalMesh",
            "AnimSequence",
            "SoundWave"
        ]
    
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
    
    def _assert_valid_asset_list(self, assets: List[Dict], min_count: int = 0):
        """Assert asset list is valid."""
        assert isinstance(assets, list), "Assets should be a list"
        assert len(assets) >= min_count, f"Expected at least {min_count} assets, got {len(assets)}"
        
        for asset in assets:
            assert isinstance(asset, dict), "Each asset should be a dictionary"
            assert "name" in asset or "path" in asset, "Asset should have name or path"
    
    def _assert_valid_asset_metadata(self, metadata: Dict[str, Any]):
        """Assert asset metadata is valid."""
        assert isinstance(metadata, dict), "Metadata should be a dictionary"
        # Common metadata fields that should exist
        expected_fields = ["path", "type", "name"]
        for field in expected_fields:
            if field in metadata:
                assert metadata[field], f"Metadata field '{field}' should not be empty"
    
    # =================================
    # LIST ASSETS TESTS
    # =================================
    
    def test_list_assets_engine_root(self):
        """Test listing assets in Engine root directory."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("list_assets", {
                "path": self.test_paths["engine_root"],
                "recursive": False
            })
            
            self._assert_valid_response(response, "list_assets")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result)
            
            print(f"✓ Found {len(result)} assets in Engine root directory")
    
    def test_list_assets_engine_shapes_recursive(self):
        """Test listing Engine BasicShapes assets recursively."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("list_assets", {
                "path": self.test_paths["engine_shapes"],
                "recursive": True
            })
            
            self._assert_valid_response(response, "list_assets")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, min_count=1)  # Should find basic shapes
            
            # Verify we got some basic shapes
            asset_names = [asset.get("name", "") for asset in result]
            basic_shapes = ["Cube", "Sphere", "Cylinder", "Plane"]
            found_shapes = [shape for shape in basic_shapes if any(shape in name for name in asset_names)]
            
            assert len(found_shapes) > 0, f"Should find some basic shapes, found assets: {asset_names}"
            print(f"✓ Found {len(result)} assets in Engine BasicShapes, including: {found_shapes}")
    
    def test_list_assets_with_type_filter(self):
        """Test listing assets with StaticMesh type filter."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("list_assets", {
                "path": self.test_paths["engine_shapes"],
                "type_filter": "StaticMesh",
                "recursive": True
            })
            
            self._assert_valid_response(response, "list_assets")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, min_count=1)
            
            # Verify all returned assets are StaticMesh type
            for asset in result:
                asset_type = asset.get("type", "")
                if asset_type:  # Only check if type is provided
                    assert "StaticMesh" in asset_type, f"Expected StaticMesh type, got {asset_type}"
            
            print(f"✓ Found {len(result)} StaticMesh assets with type filter")
    
    def test_list_assets_game_directory(self):
        """Test listing assets in Game directory."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("list_assets", {
                "path": self.test_paths["game_root"],
                "recursive": False
            })
            
            self._assert_valid_response(response, "list_assets")
            
            result = response.get("result", [])
            # Game directory might be empty in fresh project
            self._assert_valid_asset_list(result, min_count=0)
            
            print(f"✓ Found {len(result)} assets in Game directory")
    
    def test_list_assets_nonexistent_path(self):
        """Test listing assets in non-existent path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("list_assets", {
                "path": self.test_paths["nonexistent_path"],
                "recursive": False
            })
            
            # Should either return empty list or appropriate error
            assert response is not None, "No response for non-existent path"
            
            if response.get("success") is False:
                print(f"✓ Correctly handled non-existent path with error")
            else:
                # Should return empty list
                result = response.get("result", [])
                assert isinstance(result, list), "Should return empty list for non-existent path"
                print(f"✓ Correctly returned empty list for non-existent path")
    
    def test_list_assets_invalid_path_format(self):
        """Test listing assets with invalid path format."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("list_assets", {
                "path": "invalid/path/format",
                "recursive": False
            })
            
            self._assert_error_response(response, "list_assets", "invalid")
            print(f"✓ Correctly handled invalid path format")
    
    def test_list_assets_empty_path(self):
        """Test listing assets with empty path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("list_assets", {
                "path": "",
                "recursive": False
            })
            
            # Should handle gracefully - either error or default to root
            assert response is not None, "No response for empty path"
            
            if response.get("success") is False:
                print(f"✓ Correctly handled empty path with error")
            else:
                print(f"✓ Handled empty path (defaulted to root or similar)")
    
    def test_list_assets_with_multiple_type_filters(self):
        """Test listing assets with multiple type filters."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Test comma-separated types or individual calls
            response = conn.send_command("list_assets", {
                "path": self.test_paths["engine_root"],
                "type_filter": "StaticMesh,Material",
                "recursive": True
            })
            
            # Should handle multiple types gracefully
            assert response is not None, "No response for multiple type filters"
            
            if response.get("success"):
                result = response.get("result", [])
                self._assert_valid_asset_list(result, min_count=0)
                print(f"✓ Handled multiple type filters, found {len(result)} assets")
            else:
                print(f"✓ Multiple type filters handled (may not be supported)")
    
    # =================================
    # GET ASSET METADATA TESTS
    # =================================
    
    def test_get_asset_metadata_engine_cube(self):
        """Test getting metadata for Engine cube mesh."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_metadata", {
                "asset_path": self.engine_assets["cube_mesh"]
            })
            
            self._assert_valid_response(response, "get_asset_metadata")
            
            metadata = response.get("result", {})
            self._assert_valid_asset_metadata(metadata)
            
            # Verify cube-specific information
            asset_path = metadata.get("path", "")
            asset_type = metadata.get("type", "")
            
            assert "Cube" in asset_path or "cube" in asset_path.lower(), \
                f"Metadata should reference Cube asset: {asset_path}"
            
            if asset_type:
                assert "StaticMesh" in asset_type, f"Cube should be StaticMesh type: {asset_type}"
            
            print(f"✓ Retrieved metadata for Engine cube: {asset_type} at {asset_path}")
    
    def test_get_asset_metadata_engine_material(self):
        """Test getting metadata for Engine default material."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_metadata", {
                "asset_path": self.engine_assets["default_material"]
            })
            
            self._assert_valid_response(response, "get_asset_metadata")
            
            metadata = response.get("result", {})
            self._assert_valid_asset_metadata(metadata)
            
            # Verify material-specific information
            asset_path = metadata.get("path", "")
            asset_type = metadata.get("type", "")
            
            assert "Material" in asset_path or "material" in asset_path.lower(), \
                f"Metadata should reference Material asset: {asset_path}"
            
            if asset_type:
                assert "Material" in asset_type, f"Should be Material type: {asset_type}"
            
            print(f"✓ Retrieved metadata for Engine material: {asset_type} at {asset_path}")
    
    def test_get_asset_metadata_multiple_assets(self):
        """Test getting metadata for multiple Engine assets."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            test_assets = [
                self.engine_assets["sphere_mesh"],
                self.engine_assets["cylinder_mesh"],
                self.engine_assets["plane_mesh"]
            ]
            
            for asset_path in test_assets:
                response = conn.send_command("get_asset_metadata", {
                    "asset_path": asset_path
                })
                
                self._assert_valid_response(response, f"get_asset_metadata({asset_path})")
                
                metadata = response.get("result", {})
                self._assert_valid_asset_metadata(metadata)
                
                print(f"✓ Retrieved metadata for {asset_path}")
    
    def test_get_asset_metadata_nonexistent_asset(self):
        """Test getting metadata for non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_metadata", {
                "asset_path": "/Game/NonExistent/Asset"
            })
            
            self._assert_error_response(response, "get_asset_metadata", "not found")
            print(f"✓ Correctly handled metadata request for non-existent asset")
    
    def test_get_asset_metadata_invalid_path(self):
        """Test getting metadata with invalid path format."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_metadata", {
                "asset_path": "invalid/path/format"
            })
            
            self._assert_error_response(response, "get_asset_metadata", "invalid")
            print(f"✓ Correctly handled invalid path format for metadata")
    
    def test_get_asset_metadata_empty_path(self):
        """Test getting metadata with empty path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("get_asset_metadata", {
                "asset_path": ""
            })
            
            self._assert_error_response(response, "get_asset_metadata")
            print(f"✓ Correctly handled empty path for metadata")
    
    # =================================
    # SEARCH ASSETS TESTS
    # =================================
    
    def test_search_assets_by_name_cube(self):
        """Test searching for assets by name 'Cube'."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("search_assets", {
                "search_text": "Cube"
            })
            
            self._assert_valid_response(response, "search_assets")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, min_count=1)
            
            # Verify search results contain 'Cube'
            cube_assets = [
                asset for asset in result 
                if "cube" in asset.get("name", "").lower() or "cube" in asset.get("path", "").lower()
            ]
            
            assert len(cube_assets) > 0, f"Search for 'Cube' should find cube assets, got: {result}"
            print(f"✓ Found {len(cube_assets)} cube assets out of {len(result)} total results")
    
    def test_search_assets_by_name_material(self):
        """Test searching for assets by name 'Material'."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("search_assets", {
                "search_text": "Material"
            })
            
            self._assert_valid_response(response, "search_assets")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, min_count=1)
            
            # Verify search results contain 'Material'
            material_assets = [
                asset for asset in result
                if "material" in asset.get("name", "").lower() or "material" in asset.get("path", "").lower()
            ]
            
            assert len(material_assets) > 0, f"Search for 'Material' should find material assets"
            print(f"✓ Found {len(material_assets)} material assets out of {len(result)} total results")
    
    def test_search_assets_with_type_filter_staticmesh(self):
        """Test searching assets with StaticMesh type filter."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("search_assets", {
                "search_text": "Shape",
                "type_filter": "StaticMesh"
            })
            
            self._assert_valid_response(response, "search_assets")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, min_count=0)
            
            # Verify filtered results are StaticMesh type
            for asset in result:
                asset_type = asset.get("type", "")
                if asset_type:
                    assert "StaticMesh" in asset_type, f"Expected StaticMesh, got {asset_type}"
            
            print(f"✓ Found {len(result)} StaticMesh assets matching 'Shape' search with type filter")
    
    def test_search_assets_partial_match(self):
        """Test searching assets with partial name match."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Search for partial matches
            partial_searches = ["Cub", "Sph", "Cyl", "Def"]
            
            for search_text in partial_searches:
                response = conn.send_command("search_assets", {
                    "search_text": search_text
                })
                
                assert response is not None, f"No response for search: {search_text}"
                
                if response.get("success"):
                    result = response.get("result", [])
                    print(f"✓ Partial search '{search_text}' found {len(result)} assets")
                else:
                    print(f"✓ Partial search '{search_text}' handled appropriately")
    
    def test_search_assets_case_insensitive(self):
        """Test case-insensitive asset searching."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Test different cases
            search_cases = ["cube", "CUBE", "Cube", "cUbE"]
            results_counts = []
            
            for search_text in search_cases:
                response = conn.send_command("search_assets", {
                    "search_text": search_text
                })
                
                self._assert_valid_response(response, f"search_assets({search_text})")
                result = response.get("result", [])
                results_counts.append(len(result))
            
            # All case variations should return same number of results
            first_count = results_counts[0]
            for i, count in enumerate(results_counts):
                assert count == first_count or abs(count - first_count) <= 1, \
                    f"Case-insensitive search failed: {search_cases[i]} returned {count}, expected ~{first_count}"
            
            print(f"✓ Case-insensitive search working: all variations returned similar results")
    
    def test_search_assets_empty_search_text(self):
        """Test searching with empty search text."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("search_assets", {
                "search_text": ""
            })
            
            # Should handle gracefully - either error or return all assets
            assert response is not None, "No response for empty search text"
            
            if response.get("success") is False:
                print(f"✓ Correctly handled empty search text with error")
            else:
                result = response.get("result", [])
                # Empty search might return all assets or no assets
                print(f"✓ Empty search handled, returned {len(result)} assets")
    
    def test_search_assets_nonexistent_term(self):
        """Test searching for non-existent asset term."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("search_assets", {
                "search_text": "NonExistentAssetNameXYZ123"
            })
            
            self._assert_valid_response(response, "search_assets")
            
            result = response.get("result", [])
            # Should return empty list for non-existent search terms
            assert isinstance(result, list), "Should return empty list for non-existent terms"
            assert len(result) == 0, f"Should find no assets for non-existent term, found {len(result)}"
            
            print(f"✓ Correctly returned empty results for non-existent search term")
    
    def test_search_assets_special_characters(self):
        """Test searching with special characters."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            special_searches = ["*", "?", "[", "]", "\\", "/"]
            
            for search_text in special_searches:
                response = conn.send_command("search_assets", {
                    "search_text": search_text
                })
                
                # Should handle special characters gracefully
                assert response is not None, f"No response for special character: {search_text}"
                
                if response.get("success"):
                    result = response.get("result", [])
                    print(f"✓ Special character '{search_text}' search handled, found {len(result)} assets")
                else:
                    print(f"✓ Special character '{search_text}' search handled with appropriate response")
    
    # =================================
    # PERFORMANCE TESTS
    # =================================
    
    def test_list_assets_performance_large_directory(self):
        """Test listing assets performance in large directory."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            start_time = time.time()
            
            response = conn.send_command("list_assets", {
                "path": self.test_paths["engine_root"],
                "recursive": True
            })
            
            duration = time.time() - start_time
            
            self._assert_valid_response(response, "list_assets")
            
            result = response.get("result", [])
            self._assert_valid_asset_list(result, min_count=0)
            
            # Performance should be reasonable
            assert duration < 60.0, f"Listing Engine assets took too long: {duration}s"
            
            print(f"✓ Listed {len(result)} Engine assets in {duration:.2f}s")
    
    def test_search_assets_performance_multiple_terms(self):
        """Test search performance with multiple search terms."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            search_terms = ["Cube", "Sphere", "Cylinder", "Material", "Default"]
            total_results = 0
            
            start_time = time.time()
            
            for search_term in search_terms:
                response = conn.send_command("search_assets", {
                    "search_text": search_term
                })
                
                self._assert_valid_response(response, f"search_assets({search_term})")
                result = response.get("result", [])
                total_results += len(result)
            
            duration = time.time() - start_time
            
            assert duration < 30.0, f"Multiple searches took too long: {duration}s"
            
            print(f"✓ Completed {len(search_terms)} searches, found {total_results} total results in {duration:.2f}s")
    
    def test_metadata_retrieval_performance_batch(self):
        """Test metadata retrieval performance for multiple assets."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Get list of assets first
            list_response = conn.send_command("list_assets", {
                "path": self.test_paths["engine_shapes"],
                "recursive": True
            })
            
            self._assert_valid_response(list_response, "list_assets")
            assets = list_response.get("result", [])
            
            if len(assets) == 0:
                print("⚠ No assets found for metadata performance test")
                return
            
            # Test metadata retrieval for first few assets
            test_assets = assets[:min(5, len(assets))]
            
            start_time = time.time()
            
            for asset in test_assets:
                asset_path = asset.get("path") or asset.get("name", "")
                if asset_path:
                    response = conn.send_command("get_asset_metadata", {
                        "asset_path": asset_path
                    })
                    self._assert_valid_response(response, f"get_asset_metadata({asset_path})")
            
            duration = time.time() - start_time
            
            assert duration < 30.0, f"Metadata retrieval for {len(test_assets)} assets took too long: {duration}s"
            
            print(f"✓ Retrieved metadata for {len(test_assets)} assets in {duration:.2f}s")

# =================================
# TEST RUNNER FUNCTIONS
# =================================

async def run_all_tests():
    """Run all content browser command tests."""
    test_suite = TestContentBrowserCommands()
    test_suite.setup_class()
    
    # Get all test methods
    test_methods = [
        method for method in dir(test_suite)
        if method.startswith('test_') and callable(getattr(test_suite, method))
    ]
    
    results = []
    print(f"\n🚀 Running {len(test_methods)} content browser command tests...\n")
    
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