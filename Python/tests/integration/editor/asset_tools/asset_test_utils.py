"""
Test utilities for asset management testing.

Provides common utilities for:
- Asset cleanup and management
- Asset validation and verification
- Test data generation and preparation
- Performance monitoring and analysis
- Error handling and recovery
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
import sys

# Add parent directories to path
test_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(test_dir))
sys.path.insert(0, str(test_dir.parent))

from tests.test_framework import TestFramework, create_test_config
from tests.data.test_data import get_test_data_manager, AssetTestData
from unreal_mcp_server import get_unreal_connection

logger = logging.getLogger(__name__)

class AssetTestUtils:
    """Utility class for asset management testing."""
    
    def __init__(self, config=None):
        self.config = config or create_test_config()
        self.framework = TestFramework(self.config)
        self.test_data_manager = get_test_data_manager()
        self.created_assets = set()  # Track assets created during testing
        self.temp_files = []  # Track temporary files for cleanup
        
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup_all()
    
    # =================================
    # ASSET VALIDATION METHODS
    # =================================
    
    def validate_asset_path(self, asset_path: str) -> bool:
        """Validate that an asset path follows Unreal conventions."""
        if not asset_path:
            return False
        
        # Must start with /Game or /Engine
        if not (asset_path.startswith("/Game") or asset_path.startswith("/Engine")):
            return False
        
        # Should not contain invalid characters
        invalid_chars = ['<', '>', '"', '|', '?', '*', '\\']
        if any(char in asset_path for char in invalid_chars):
            return False
        
        # Should not end with /
        if asset_path.endswith('/'):
            return False
        
        return True
    
    def validate_asset_response(self, response: Dict[str, Any], command: str) -> Tuple[bool, str]:
        """Validate that an asset command response is properly formatted."""
        if not response:
            return False, f"{command}: No response received"
        
        if not isinstance(response, dict):
            return False, f"{command}: Response is not a dictionary"
        
        # Check for error conditions
        if response.get("status") == "error":
            error_msg = response.get("error", "Unknown error")
            return False, f"{command}: Command failed - {error_msg}"
        
        if response.get("success") is False:
            error_msg = response.get("error", response.get("message", "Unknown error"))
            return False, f"{command}: Command failed - {error_msg}"
        
        return True, "Valid response"
    
    def validate_asset_list(self, assets: List[Dict], min_count: int = 0) -> Tuple[bool, str]:
        """Validate that an asset list is properly formatted."""
        if not isinstance(assets, list):
            return False, "Assets should be a list"
        
        if len(assets) < min_count:
            return False, f"Expected at least {min_count} assets, got {len(assets)}"
        
        for i, asset in enumerate(assets):
            if not isinstance(asset, dict):
                return False, f"Asset {i} should be a dictionary"
            
            if not ("name" in asset or "path" in asset):
                return False, f"Asset {i} should have name or path"
        
        return True, "Valid asset list"
    
    def validate_asset_metadata(self, metadata: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate that asset metadata is properly formatted."""
        if not isinstance(metadata, dict):
            return False, "Metadata should be a dictionary"
        
        # Check for required fields
        required_fields = ["path", "type", "name"]
        missing_fields = []
        
        for field in required_fields:
            if field not in metadata:
                # Some fields might be optional depending on the asset
                continue
            if not metadata[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Metadata missing or empty fields: {', '.join(missing_fields)}"
        
        return True, "Valid asset metadata"
    
    # =================================
    # ASSET CREATION AND MANAGEMENT
    # =================================
    
    def create_test_asset_by_duplication(self, source_path: str, dest_path: str) -> bool:
        """Create a test asset by duplicating an existing asset."""
        with self.framework.test_connection() as conn:
            if not conn.connect():
                logger.error("Failed to connect for asset duplication")
                return False
            
            response = conn.send_command("duplicate_asset", {
                "source_path": source_path,
                "destination_path": dest_path
            })
            
            is_valid, message = self.validate_asset_response(response, "duplicate_asset")
            if is_valid:
                self.created_assets.add(dest_path)
                logger.info(f"Created test asset: {dest_path}")
                return True
            else:
                logger.error(f"Failed to create test asset: {message}")
                return False
    
    def create_temp_file(self, content: bytes, suffix: str = ".txt") -> str:
        """Create a temporary file for import testing."""
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            temp_file.write(content)
            temp_file.close()
            
            self.temp_files.append(temp_file.name)
            logger.info(f"Created temporary file: {temp_file.name}")
            return temp_file.name
        except Exception as e:
            logger.error(f"Failed to create temporary file: {e}")
            return ""
    
    def asset_exists(self, asset_path: str) -> bool:
        """Check if an asset exists in the project."""
        with self.framework.test_connection() as conn:
            if not conn.connect():
                return False
            
            # Try to get metadata for the asset
            response = conn.send_command("get_asset_metadata", {
                "asset_path": asset_path
            })
            
            return response and response.get("success") is not False and response.get("status") != "error"
    
    def wait_for_asset(self, asset_path: str, timeout: float = 10.0) -> bool:
        """Wait for an asset to be available (useful after creation operations)."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.asset_exists(asset_path):
                return True
            time.sleep(0.1)
        
        return False
    
    # =================================
    # ASSET CLEANUP METHODS
    # =================================
    
    def cleanup_asset(self, asset_path: str) -> bool:
        """Clean up a single asset."""
        try:
            with self.framework.test_connection() as conn:
                if not conn.connect():
                    logger.error("Failed to connect for asset cleanup")
                    return False
                
                response = conn.send_command("delete_asset", {"asset_path": asset_path})
                
                if response and (response.get("success") or response.get("status") != "error"):
                    logger.info(f"Cleaned up asset: {asset_path}")
                    return True
                else:
                    logger.warning(f"Failed to cleanup asset {asset_path}: {response}")
                    return False
        except Exception as e:
            logger.error(f"Error cleaning up asset {asset_path}: {e}")
            return False
    
    def cleanup_created_assets(self):
        """Clean up all assets created during testing."""
        if not self.created_assets:
            return
        
        logger.info(f"Cleaning up {len(self.created_assets)} created assets...")
        
        cleanup_count = 0
        for asset_path in list(self.created_assets):
            if self.cleanup_asset(asset_path):
                cleanup_count += 1
                self.created_assets.remove(asset_path)
        
        logger.info(f"Successfully cleaned up {cleanup_count} assets")
        
        if self.created_assets:
            logger.warning(f"Failed to cleanup {len(self.created_assets)} assets: {list(self.created_assets)}")
    
    def cleanup_temp_files(self):
        """Clean up all temporary files created during testing."""
        if not self.temp_files:
            return
        
        logger.info(f"Cleaning up {len(self.temp_files)} temporary files...")
        
        cleanup_count = 0
        for temp_file in list(self.temp_files):
            try:
                os.unlink(temp_file)
                cleanup_count += 1
                self.temp_files.remove(temp_file)
                logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.error(f"Failed to cleanup temp file {temp_file}: {e}")
        
        logger.info(f"Successfully cleaned up {cleanup_count} temp files")
    
    def cleanup_all(self):
        """Clean up all resources created during testing."""
        logger.info("Starting comprehensive cleanup...")
        self.cleanup_created_assets()
        self.cleanup_temp_files()
        logger.info("Cleanup complete")
    
    # =================================
    # PERFORMANCE MONITORING
    # =================================
    
    def measure_command_performance(self, command: str, params: Dict[str, Any], 
                                  expected_max_duration: float = 30.0) -> Tuple[Dict[str, Any], float, bool]:
        """Measure the performance of a command execution."""
        with self.framework.test_connection() as conn:
            if not conn.connect():
                return {}, 0.0, False
            
            start_time = time.time()
            response = conn.send_command(command, params)
            duration = time.time() - start_time
            
            within_expected = duration <= expected_max_duration
            
            logger.info(f"Command {command} took {duration:.2f}s (expected: <{expected_max_duration}s)")
            
            return response, duration, within_expected
    
    def benchmark_asset_operations(self, asset_path: str) -> Dict[str, float]:
        """Benchmark common operations on an asset."""
        benchmarks = {}
        
        with self.framework.test_connection() as conn:
            if not conn.connect():
                return benchmarks
            
            # Benchmark load_asset
            start_time = time.time()
            response = conn.send_command("load_asset", {"asset_path": asset_path})
            if response and response.get("success") is not False:
                benchmarks["load_asset"] = time.time() - start_time
            
            # Benchmark get_asset_metadata
            start_time = time.time()
            response = conn.send_command("get_asset_metadata", {"asset_path": asset_path})
            if response and response.get("success") is not False:
                benchmarks["get_asset_metadata"] = time.time() - start_time
            
            # Benchmark save_asset
            start_time = time.time()
            response = conn.send_command("save_asset", {"asset_path": asset_path})
            if response and response.get("success") is not False:
                benchmarks["save_asset"] = time.time() - start_time
        
        return benchmarks
    
    # =================================
    # TEST DATA GENERATION
    # =================================
    
    def generate_unique_asset_path(self, base_path: str = "/Game/TestAssets", 
                                 asset_name: str = "TestAsset") -> str:
        """Generate a unique asset path for testing."""
        import random
        timestamp = int(time.time() * 1000)  # milliseconds
        random_suffix = random.randint(1000, 9999)
        unique_name = f"{asset_name}_{timestamp}_{random_suffix}"
        return f"{base_path}/{unique_name}"
    
    def get_engine_assets_for_testing(self) -> List[str]:
        """Get a list of Engine assets safe for testing."""
        engine_assets = self.test_data_manager.get_engine_assets()
        return [asset.path for asset in engine_assets.values()]
    
    def prepare_test_assets(self, count: int = 3) -> List[str]:
        """Prepare a set of test assets by duplication."""
        engine_assets = self.get_engine_assets_for_testing()
        test_assets = []
        
        for i in range(min(count, len(engine_assets))):
            source_path = engine_assets[i]
            dest_path = self.generate_unique_asset_path(asset_name=f"PreparedAsset_{i}")
            
            if self.create_test_asset_by_duplication(source_path, dest_path):
                test_assets.append(dest_path)
        
        return test_assets
    
    # =================================
    # ERROR ANALYSIS AND RECOVERY
    # =================================
    
    def analyze_error_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an error response and provide diagnostic information."""
        analysis = {
            "error_type": "unknown",
            "error_message": "",
            "suggested_action": "review logs and retry",
            "recoverable": False
        }
        
        if not response:
            analysis["error_type"] = "no_response"
            analysis["error_message"] = "No response received from Unreal Engine"
            analysis["suggested_action"] = "check connection and retry"
            return analysis
        
        error_msg = response.get("error", "").lower()
        
        # Categorize common errors
        if "not found" in error_msg or "does not exist" in error_msg:
            analysis["error_type"] = "asset_not_found"
            analysis["error_message"] = "Asset does not exist"
            analysis["suggested_action"] = "verify asset path and ensure asset exists"
            analysis["recoverable"] = True
        elif "timeout" in error_msg or "connection" in error_msg:
            analysis["error_type"] = "connection_issue"
            analysis["error_message"] = "Connection or timeout issue"
            analysis["suggested_action"] = "check Unreal Engine connection and retry"
            analysis["recoverable"] = True
        elif "invalid" in error_msg or "malformed" in error_msg:
            analysis["error_type"] = "invalid_input"
            analysis["error_message"] = "Invalid input parameters"
            analysis["suggested_action"] = "validate input parameters and format"
            analysis["recoverable"] = True
        elif "permission" in error_msg or "access denied" in error_msg:
            analysis["error_type"] = "permission_denied"
            analysis["error_message"] = "Permission or access issue"
            analysis["suggested_action"] = "check file/asset permissions"
            analysis["recoverable"] = False
        
        analysis["error_message"] = response.get("error", analysis["error_message"])
        
        return analysis
    
    def attempt_error_recovery(self, command: str, params: Dict[str, Any], 
                             error_response: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Attempt to recover from an error by retrying with modifications."""
        analysis = self.analyze_error_response(error_response)
        
        if not analysis["recoverable"]:
            logger.warning(f"Error not recoverable for {command}: {analysis['error_message']}")
            return None
        
        for attempt in range(max_retries):
            logger.info(f"Recovery attempt {attempt + 1} for {command}")
            
            # Add delay between retries
            if attempt > 0:
                time.sleep(1.0)
            
            with self.framework.test_connection() as conn:
                if not conn.connect():
                    continue
                
                try:
                    response = conn.send_command(command, params)
                    
                    if response and response.get("success") is not False and response.get("status") != "error":
                        logger.info(f"Recovery successful for {command} on attempt {attempt + 1}")
                        return response
                        
                except Exception as e:
                    logger.warning(f"Recovery attempt {attempt + 1} failed: {e}")
                    continue
        
        logger.error(f"Recovery failed for {command} after {max_retries} attempts")
        return None
    
    # =================================
    # BATCH OPERATIONS
    # =================================
    
    def batch_validate_assets(self, asset_paths: List[str]) -> Dict[str, bool]:
        """Validate multiple assets in batch."""
        results = {}
        
        with self.framework.test_connection() as conn:
            if not conn.connect():
                return {path: False for path in asset_paths}
            
            for asset_path in asset_paths:
                try:
                    response = conn.send_command("get_asset_metadata", {"asset_path": asset_path})
                    results[asset_path] = (response and 
                                         response.get("success") is not False and 
                                         response.get("status") != "error")
                except Exception as e:
                    logger.error(f"Error validating {asset_path}: {e}")
                    results[asset_path] = False
        
        return results
    
    def batch_cleanup_assets(self, asset_paths: List[str]) -> Dict[str, bool]:
        """Clean up multiple assets in batch."""
        results = {}
        
        with self.framework.test_connection() as conn:
            if not conn.connect():
                return {path: False for path in asset_paths}
            
            for asset_path in asset_paths:
                results[asset_path] = self.cleanup_asset(asset_path)
        
        return results

# =================================
# CONVENIENCE FUNCTIONS
# =================================

def create_asset_test_utils(config=None) -> AssetTestUtils:
    """Create asset test utilities with configuration."""
    return AssetTestUtils(config)

def validate_engine_assets() -> Dict[str, bool]:
    """Validate that all expected Engine assets are available."""
    utils = AssetTestUtils()
    engine_assets = utils.get_engine_assets_for_testing()
    return utils.batch_validate_assets(engine_assets)

def prepare_clean_test_environment() -> AssetTestUtils:
    """Prepare a clean test environment with utilities."""
    utils = AssetTestUtils()
    logger.info("Test environment prepared")
    return utils

if __name__ == "__main__":
    # Test utility functions when run directly
    logging.basicConfig(level=logging.INFO)
    
    print("Testing AssetTestUtils...")
    
    with create_asset_test_utils() as utils:
        print(f"✓ AssetTestUtils created")
        
        # Test Engine asset validation
        engine_validation = validate_engine_assets()
        available_count = sum(1 for available in engine_validation.values() if available)
        print(f"✓ Engine assets validation: {available_count}/{len(engine_validation)} available")
        
        # Test path validation
        valid_paths = [
            "/Game/TestAssets/ValidAsset",
            "/Engine/BasicShapes/Cube"
        ]
        invalid_paths = [
            "invalid/path",
            "/Game/Invalid<>Asset",
            "/Game/TrailingSlash/",
            ""
        ]
        
        for path in valid_paths:
            assert utils.validate_asset_path(path), f"Should be valid: {path}"
        
        for path in invalid_paths:
            assert not utils.validate_asset_path(path), f"Should be invalid: {path}"
        
        print(f"✓ Asset path validation working correctly")
        
        print(f"✓ All AssetTestUtils tests passed!")