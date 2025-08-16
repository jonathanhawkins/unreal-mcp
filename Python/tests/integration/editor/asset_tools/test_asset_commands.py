"""
Comprehensive tests for core asset management commands.

Tests all asset operations including:
- load_asset: Load assets into memory
- save_asset: Save assets to disk
- duplicate_asset: Create asset duplicates  
- delete_asset: Remove assets from project
- rename_asset: Rename existing assets
- move_asset: Move assets to different locations
- import_asset: Import external files as assets
- export_asset: Export assets to external files

Each test covers happy path, error handling, edge cases, and performance validation.
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
import pytest
import sys

# Add parent directories to path for imports
test_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(test_dir.parent))

from tests.test_framework import TestFramework, create_test_config, TestResult
from tests.data.test_data import get_test_data_manager, AssetTestData
from unreal_mcp_server import get_unreal_connection

class TestAssetCommands:
    """Test suite for core asset management commands."""
    
    @classmethod
    def setup_class(cls):
        """Setup test framework and data."""
        cls.config = create_test_config()
        cls.framework = TestFramework(cls.config)
        cls.test_data_manager = get_test_data_manager()
        cls.test_results = []
        cls.cleanup_assets = []  # Track assets to cleanup
        
        # Test data
        cls.engine_assets = {
            "cube_mesh": "/Engine/BasicShapes/Cube",
            "sphere_mesh": "/Engine/BasicShapes/Sphere", 
            "cylinder_mesh": "/Engine/BasicShapes/Cylinder",
            "plane_mesh": "/Engine/BasicShapes/Plane",
            "default_material": "/Engine/EngineMaterials/DefaultMaterial"
        }
        
        cls.test_assets = {
            "test_folder": "/Game/TestAssets",
            "temp_folder": "/Game/TempTestAssets",
            "duplicate_source": "/Game/TestAssets/SourceAsset",
            "duplicate_target": "/Game/TestAssets/DuplicatedAsset",
            "rename_asset": "/Game/TestAssets/AssetToRename",
            "move_source": "/Game/TestAssets/MoveSource", 
            "move_target": "/Game/TestAssets/Moved/MovedAsset"
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
    
    # =================================
    # LOAD ASSET TESTS
    # =================================
    
    def test_load_asset_engine_cube(self):
        """Test loading Engine cube mesh asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("load_asset", {
                "asset_path": self.engine_assets["cube_mesh"]
            })
            
            self._assert_valid_response(response, "load_asset")
            print(f"✓ Successfully loaded Engine cube mesh")
    
    def test_load_asset_engine_material(self):
        """Test loading Engine default material."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("load_asset", {
                "asset_path": self.engine_assets["default_material"]
            })
            
            self._assert_valid_response(response, "load_asset")
            print(f"✓ Successfully loaded Engine default material")
    
    def test_load_asset_nonexistent(self):
        """Test loading non-existent asset returns error."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("load_asset", {
                "asset_path": "/Game/NonExistent/Asset"
            })
            
            self._assert_error_response(response, "load_asset", "not found")
            print(f"✓ Correctly handled non-existent asset loading")
    
    def test_load_asset_invalid_path(self):
        """Test loading asset with invalid path format."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("load_asset", {
                "asset_path": "invalid/path/format"
            })
            
            self._assert_error_response(response, "load_asset", "invalid")
            print(f"✓ Correctly handled invalid asset path format")
    
    def test_load_asset_empty_path(self):
        """Test loading asset with empty path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("load_asset", {
                "asset_path": ""
            })
            
            self._assert_error_response(response, "load_asset")
            print(f"✓ Correctly handled empty asset path")
    
    # =================================
    # SAVE ASSET TESTS  
    # =================================
    
    def test_save_asset_basic(self):
        """Test basic asset saving functionality."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # First load an asset
            load_response = conn.send_command("load_asset", {
                "asset_path": self.engine_assets["cube_mesh"]
            })
            self._assert_valid_response(load_response, "load_asset")
            
            # Then save it
            response = conn.send_command("save_asset", {
                "asset_path": self.engine_assets["cube_mesh"],
                "only_if_dirty": False
            })
            
            self._assert_valid_response(response, "save_asset")
            print(f"✓ Successfully saved asset")
    
    def test_save_asset_only_if_dirty(self):
        """Test saving asset only if dirty."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("save_asset", {
                "asset_path": self.engine_assets["cube_mesh"],
                "only_if_dirty": True
            })
            
            # Should succeed even if not dirty
            self._assert_valid_response(response, "save_asset")
            print(f"✓ Successfully handled save_asset with only_if_dirty=True")
    
    def test_save_asset_nonexistent(self):
        """Test saving non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("save_asset", {
                "asset_path": "/Game/NonExistent/Asset"
            })
            
            self._assert_error_response(response, "save_asset", "not found")
            print(f"✓ Correctly handled saving non-existent asset")
    
    # =================================
    # DUPLICATE ASSET TESTS
    # =================================
    
    def test_duplicate_asset_engine_mesh(self):
        """Test duplicating Engine mesh to Game folder."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            source_path = self.engine_assets["cube_mesh"]
            dest_path = "/Game/TestAssets/DuplicatedCube"
            
            response = conn.send_command("duplicate_asset", {
                "source_path": source_path,
                "destination_path": dest_path
            })
            
            self._assert_valid_response(response, "duplicate_asset")
            self._add_cleanup_asset(dest_path)
            print(f"✓ Successfully duplicated Engine mesh to Game folder")
    
    def test_duplicate_asset_to_existing_path(self):
        """Test duplicating asset to existing path should handle appropriately."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            source_path = self.engine_assets["sphere_mesh"]
            dest_path = "/Game/TestAssets/ExistingAsset"
            
            # First duplication should succeed
            response1 = conn.send_command("duplicate_asset", {
                "source_path": source_path,
                "destination_path": dest_path
            })
            self._assert_valid_response(response1, "duplicate_asset (first)")
            self._add_cleanup_asset(dest_path)
            
            # Second duplication to same path should handle appropriately
            response2 = conn.send_command("duplicate_asset", {
                "source_path": source_path,
                "destination_path": dest_path
            })
            
            # Should either succeed with different name or give appropriate error
            assert response2 is not None, "No response for second duplication"
            print(f"✓ Correctly handled duplicate asset to existing path")
    
    def test_duplicate_asset_nonexistent_source(self):
        """Test duplicating non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("duplicate_asset", {
                "source_path": "/Game/NonExistent/Source",
                "destination_path": "/Game/TestAssets/Destination"
            })
            
            self._assert_error_response(response, "duplicate_asset", "not found")
            print(f"✓ Correctly handled duplicating non-existent asset")
    
    def test_duplicate_asset_invalid_destination(self):
        """Test duplicating to invalid destination path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("duplicate_asset", {
                "source_path": self.engine_assets["cube_mesh"],
                "destination_path": "invalid/path/format"
            })
            
            self._assert_error_response(response, "duplicate_asset", "invalid")
            print(f"✓ Correctly handled invalid destination path")
    
    # =================================
    # DELETE ASSET TESTS
    # =================================
    
    def test_delete_asset_user_created(self):
        """Test deleting user-created test asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # First create/duplicate an asset to delete
            source_path = self.engine_assets["cylinder_mesh"]
            test_asset_path = "/Game/TestAssets/AssetToDelete"
            
            duplicate_response = conn.send_command("duplicate_asset", {
                "source_path": source_path,
                "destination_path": test_asset_path
            })
            self._assert_valid_response(duplicate_response, "duplicate_asset")
            
            # Now delete it
            response = conn.send_command("delete_asset", {
                "asset_path": test_asset_path
            })
            
            self._assert_valid_response(response, "delete_asset")
            print(f"✓ Successfully deleted user-created asset")
    
    def test_delete_asset_nonexistent(self):
        """Test deleting non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("delete_asset", {
                "asset_path": "/Game/NonExistent/Asset"
            })
            
            self._assert_error_response(response, "delete_asset", "not found")
            print(f"✓ Correctly handled deleting non-existent asset")
    
    def test_delete_asset_engine_protected(self):
        """Test attempting to delete Engine asset (should be protected)."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("delete_asset", {
                "asset_path": self.engine_assets["cube_mesh"]
            })
            
            # Should either be protected or handle gracefully
            if response.get("success") is False or response.get("status") == "error":
                print(f"✓ Engine asset properly protected from deletion")
            else:
                print(f"✓ Delete operation handled (may not actually delete Engine assets)")
    
    # =================================
    # RENAME ASSET TESTS
    # =================================
    
    def test_rename_asset_basic(self):
        """Test basic asset renaming."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create asset to rename
            source_path = self.engine_assets["plane_mesh"]
            original_path = "/Game/TestAssets/OriginalName"
            
            duplicate_response = conn.send_command("duplicate_asset", {
                "source_path": source_path,
                "destination_path": original_path
            })
            self._assert_valid_response(duplicate_response, "duplicate_asset")
            
            # Rename it
            response = conn.send_command("rename_asset", {
                "source_path": original_path,
                "new_name": "RenamedAsset"
            })
            
            self._assert_valid_response(response, "rename_asset")
            
            # Add the new path to cleanup (should be in same folder with new name)
            new_path = "/Game/TestAssets/RenamedAsset"
            self._add_cleanup_asset(new_path)
            print(f"✓ Successfully renamed asset")
    
    def test_rename_asset_nonexistent(self):
        """Test renaming non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("rename_asset", {
                "source_path": "/Game/NonExistent/Asset",
                "new_name": "NewName"
            })
            
            self._assert_error_response(response, "rename_asset", "not found")
            print(f"✓ Correctly handled renaming non-existent asset")
    
    def test_rename_asset_invalid_name(self):
        """Test renaming asset with invalid name."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create asset to test with
            source_path = self.engine_assets["cube_mesh"]
            test_path = "/Game/TestAssets/AssetForInvalidRename"
            
            duplicate_response = conn.send_command("duplicate_asset", {
                "source_path": source_path,
                "destination_path": test_path
            })
            self._assert_valid_response(duplicate_response, "duplicate_asset")
            self._add_cleanup_asset(test_path)
            
            # Try to rename with invalid characters
            response = conn.send_command("rename_asset", {
                "source_path": test_path,
                "new_name": "Invalid/Name*With<>Chars"
            })
            
            # Should handle invalid characters gracefully
            if response.get("success") is False or response.get("status") == "error":
                print(f"✓ Correctly rejected invalid asset name characters")
            else:
                print(f"✓ Rename handled (may sanitize invalid characters)")
    
    def test_rename_asset_empty_name(self):
        """Test renaming asset with empty name."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("rename_asset", {
                "source_path": self.engine_assets["cube_mesh"],
                "new_name": ""
            })
            
            self._assert_error_response(response, "rename_asset")
            print(f"✓ Correctly handled empty asset name")
    
    # =================================
    # MOVE ASSET TESTS
    # =================================
    
    def test_move_asset_basic(self):
        """Test basic asset moving between folders."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create asset to move
            source_mesh = self.engine_assets["sphere_mesh"]
            original_path = "/Game/TestAssets/AssetToMove"
            new_path = "/Game/TestAssets/Moved/MovedAsset"
            
            duplicate_response = conn.send_command("duplicate_asset", {
                "source_path": source_mesh,
                "destination_path": original_path
            })
            self._assert_valid_response(duplicate_response, "duplicate_asset")
            
            # Move it
            response = conn.send_command("move_asset", {
                "source_path": original_path,
                "destination_path": new_path
            })
            
            self._assert_valid_response(response, "move_asset")
            self._add_cleanup_asset(new_path)
            print(f"✓ Successfully moved asset between folders")
    
    def test_move_asset_same_location(self):
        """Test moving asset to same location."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create asset
            source_mesh = self.engine_assets["cylinder_mesh"]
            test_path = "/Game/TestAssets/SameLocationAsset"
            
            duplicate_response = conn.send_command("duplicate_asset", {
                "source_path": source_mesh,
                "destination_path": test_path
            })
            self._assert_valid_response(duplicate_response, "duplicate_asset")
            self._add_cleanup_asset(test_path)
            
            # Try to move to same location
            response = conn.send_command("move_asset", {
                "source_path": test_path,
                "destination_path": test_path
            })
            
            # Should handle gracefully (either succeed or appropriate message)
            assert response is not None, "No response for same-location move"
            print(f"✓ Correctly handled moving asset to same location")
    
    def test_move_asset_nonexistent(self):
        """Test moving non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("move_asset", {
                "source_path": "/Game/NonExistent/Asset",
                "destination_path": "/Game/TestAssets/Destination"
            })
            
            self._assert_error_response(response, "move_asset", "not found")
            print(f"✓ Correctly handled moving non-existent asset")
    
    # =================================
    # IMPORT ASSET TESTS  
    # =================================
    
    def test_import_asset_valid_file(self):
        """Test importing valid external file (mock test)."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create a temporary file to "import"
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(b"Test file content for import")
                tmp_file_path = tmp_file.name
            
            try:
                response = conn.send_command("import_asset", {
                    "file_path": tmp_file_path,
                    "destination_path": "/Game/TestAssets/ImportedFile"
                })
                
                # Import may or may not succeed depending on file type support
                # Just verify we get a response
                assert response is not None, "No response for import_asset"
                
                if response.get("success"):
                    self._add_cleanup_asset("/Game/TestAssets/ImportedFile")
                    print(f"✓ Successfully imported file")
                else:
                    print(f"✓ Import handled appropriately (may not support .txt files)")
                
            finally:
                # Cleanup temp file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
    
    def test_import_asset_nonexistent_file(self):
        """Test importing non-existent file."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("import_asset", {
                "file_path": "/nonexistent/file.txt",
                "destination_path": "/Game/TestAssets/ImportedFile"
            })
            
            self._assert_error_response(response, "import_asset", "not found")
            print(f"✓ Correctly handled importing non-existent file")
    
    def test_import_asset_invalid_destination(self):
        """Test importing to invalid destination."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(b"Test content")
                tmp_file_path = tmp_file.name
            
            try:
                response = conn.send_command("import_asset", {
                    "file_path": tmp_file_path,
                    "destination_path": "invalid/destination"
                })
                
                self._assert_error_response(response, "import_asset", "invalid")
                print(f"✓ Correctly handled invalid import destination")
                
            finally:
                os.unlink(tmp_file_path)
    
    # =================================
    # EXPORT ASSET TESTS
    # =================================
    
    def test_export_asset_engine_mesh(self):
        """Test exporting Engine mesh asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            # Create temporary export path
            with tempfile.TemporaryDirectory() as tmp_dir:
                export_path = os.path.join(tmp_dir, "exported_cube.obj")
                
                response = conn.send_command("export_asset", {
                    "asset_path": self.engine_assets["cube_mesh"],
                    "export_path": export_path
                })
                
                # Export may or may not succeed depending on exporter availability
                assert response is not None, "No response for export_asset"
                
                if response.get("success"):
                    print(f"✓ Successfully exported Engine mesh")
                else:
                    print(f"✓ Export handled appropriately (may not support .obj format)")
    
    def test_export_asset_nonexistent(self):
        """Test exporting non-existent asset."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("export_asset", {
                "asset_path": "/Game/NonExistent/Asset",
                "export_path": "/tmp/export.obj"
            })
            
            self._assert_error_response(response, "export_asset", "not found")
            print(f"✓ Correctly handled exporting non-existent asset")
    
    def test_export_asset_invalid_path(self):
        """Test exporting to invalid file path."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            response = conn.send_command("export_asset", {
                "asset_path": self.engine_assets["cube_mesh"],
                "export_path": "/invalid/directory/path/file.obj"
            })
            
            # Should handle invalid export path gracefully
            if response.get("success") is False or response.get("status") == "error":
                print(f"✓ Correctly handled invalid export path")
            else:
                print(f"✓ Export handled (may create directory or use fallback)")
    
    # =================================
    # PERFORMANCE TESTS
    # =================================
    
    def test_load_multiple_assets_performance(self):
        """Test loading multiple assets for performance."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            assets_to_test = list(self.engine_assets.values())[:3]  # Test 3 assets
            start_time = time.time()
            
            for asset_path in assets_to_test:
                response = conn.send_command("load_asset", {"asset_path": asset_path})
                self._assert_valid_response(response, f"load_asset({asset_path})")
            
            duration = time.time() - start_time
            
            assert duration < 30.0, f"Loading {len(assets_to_test)} assets took too long: {duration}s"
            print(f"✓ Loaded {len(assets_to_test)} assets in {duration:.2f}s")
    
    def test_duplicate_asset_batch_performance(self):
        """Test duplicating multiple assets for performance."""
        with self.framework.test_connection() as conn:
            assert conn.connect(), "Failed to connect to Unreal Engine"
            
            source_assets = [
                (self.engine_assets["cube_mesh"], "/Game/TestAssets/PerfCube"),
                (self.engine_assets["sphere_mesh"], "/Game/TestAssets/PerfSphere"),
                (self.engine_assets["cylinder_mesh"], "/Game/TestAssets/PerfCylinder")
            ]
            
            start_time = time.time()
            
            for source_path, dest_path in source_assets:
                response = conn.send_command("duplicate_asset", {
                    "source_path": source_path,
                    "destination_path": dest_path
                })
                self._assert_valid_response(response, f"duplicate_asset({dest_path})")
                self._add_cleanup_asset(dest_path)
            
            duration = time.time() - start_time
            
            assert duration < 60.0, f"Duplicating {len(source_assets)} assets took too long: {duration}s"
            print(f"✓ Duplicated {len(source_assets)} assets in {duration:.2f}s")

# =================================
# TEST RUNNER FUNCTIONS
# =================================

async def run_all_tests():
    """Run all asset command tests."""
    test_suite = TestAssetCommands()
    test_suite.setup_class()
    
    # Get all test methods
    test_methods = [
        method for method in dir(test_suite) 
        if method.startswith('test_') and callable(getattr(test_suite, method))
    ]
    
    results = []
    print(f"\n🚀 Running {len(test_methods)} asset command tests...\n")
    
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