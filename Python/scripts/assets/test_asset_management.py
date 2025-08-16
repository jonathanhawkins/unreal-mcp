#!/usr/bin/env python3
"""Test script for asset management functionality."""

import sys
import os
import asyncio
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unreal_mcp_server import get_unreal_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_asset_management():
    """Test various asset management operations."""
    
    logger.info("Testing Asset Management Commands")
    logger.info("=" * 50)
    
    # Get connection
    connection = get_unreal_connection()
    if not connection:
        logger.error("Failed to connect to Unreal Engine")
        return
    
    try:
        # Test 1: List assets in /Game directory
        logger.info("\n1. Listing assets in /Game directory...")
        result = connection.send_command("list_assets", {
            "path": "/Game",
            "recursive": False
        })
        
        if result and result.get("status") != "error":
            assets = result.get("result", {}).get("assets", [])
            logger.info(f"   Found {len(assets)} assets in /Game")
            for asset in assets[:5]:  # Show first 5
                logger.info(f"   - {asset.get('name')} ({asset.get('class')})")
        else:
            logger.error(f"   Failed to list assets: {result}")
        
        # Test 2: Search for assets
        logger.info("\n2. Searching for assets with 'Cube' in name...")
        result = connection.send_command("search_assets", {
            "search_text": "Cube"
        })
        
        if result and result.get("status") != "error":
            assets = result.get("result", {}).get("assets", [])
            logger.info(f"   Found {len(assets)} assets matching 'Cube'")
            for asset in assets:
                logger.info(f"   - {asset.get('path')}")
        else:
            logger.error(f"   Search failed: {result}")
        
        # Test 3: Get metadata for default cube
        logger.info("\n3. Getting metadata for Engine cube asset...")
        result = connection.send_command("get_asset_metadata", {
            "asset_path": "/Engine/BasicShapes/Cube"
        })
        
        if result and result.get("status") != "error":
            metadata = result.get("result", {})
            logger.info(f"   Asset Name: {metadata.get('asset_name')}")
            logger.info(f"   Package Name: {metadata.get('package_name')}")
            logger.info(f"   Class: {metadata.get('class')}")
            tags = metadata.get("tags", {})
            if tags:
                logger.info("   Tags:")
                for key, value in list(tags.items())[:5]:  # Show first 5 tags
                    logger.info(f"     - {key}: {value}")
        else:
            logger.error(f"   Failed to get metadata: {result}")
        
        # Test 4: List assets with type filter
        logger.info("\n4. Listing StaticMesh assets...")
        result = connection.send_command("list_assets", {
            "path": "/Engine/BasicShapes",
            "type_filter": "StaticMesh",
            "recursive": False
        })
        
        if result and result.get("status") != "error":
            assets = result.get("result", {}).get("assets", [])
            logger.info(f"   Found {len(assets)} StaticMesh assets")
            for asset in assets[:5]:  # Show first 5
                logger.info(f"   - {asset.get('name')}")
        else:
            logger.error(f"   Failed to list StaticMesh assets: {result}")
        
        # Test 5: Create and duplicate a test asset (if we have created one)
        logger.info("\n5. Testing asset duplication...")
        
        # First check if we have a test blueprint to duplicate
        test_blueprint_path = "/Game/TestCubeBlueprint"
        result = connection.send_command("get_asset_metadata", {
            "asset_path": test_blueprint_path
        })
        
        if result and result.get("status") != "error":
            # Blueprint exists, try to duplicate it
            duplicate_path = "/Game/TestCubeBlueprint_Copy"
            logger.info(f"   Duplicating {test_blueprint_path} to {duplicate_path}...")
            
            result = connection.send_command("duplicate_asset", {
                "source_path": test_blueprint_path,
                "destination_path": duplicate_path
            })
            
            if result and result.get("status") != "error":
                logger.info(f"   Successfully duplicated asset!")
                
                # Now delete the duplicate to clean up
                logger.info(f"   Cleaning up - deleting duplicate...")
                result = connection.send_command("delete_asset", {
                    "asset_path": duplicate_path
                })
                
                if result and result.get("status") != "error":
                    logger.info(f"   Successfully deleted duplicate asset")
                else:
                    logger.warning(f"   Failed to delete duplicate: {result}")
            else:
                logger.error(f"   Failed to duplicate asset: {result}")
        else:
            logger.info("   No test blueprint found to duplicate (run blueprint tests first)")
        
        # Test 6: Get asset references and dependencies
        logger.info("\n6. Testing asset references and dependencies...")
        
        # Check dependencies of Engine cube
        result = connection.send_command("get_asset_dependencies", {
            "asset_path": "/Engine/BasicShapes/Cube"
        })
        
        if result and result.get("status") != "error":
            deps = result.get("result", {}).get("dependencies", [])
            logger.info(f"   Cube has {len(deps)} dependencies")
            for dep in deps[:3]:  # Show first 3
                logger.info(f"   - {dep}")
        else:
            logger.error(f"   Failed to get dependencies: {result}")
        
        logger.info("\n" + "=" * 50)
        logger.info("Asset Management Tests Completed!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_asset_management())