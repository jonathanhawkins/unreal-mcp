"""Asset registry tools for Unreal Engine via MCP."""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

def register_tools(mcp, connection=None):
    """Register asset registry tools with the MCP server."""
    
    # Import get_unreal_connection from parent module
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    from unreal_mcp_server import get_unreal_connection
    
    @mcp.tool()
    async def get_asset_references(asset_path: str) -> Dict:
        """Get all assets that reference the specified asset.
        
        Args:
            asset_path: Full path to the asset
        
        Returns:
            Dictionary containing list of referencing assets
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("get_asset_references", {
            "asset_path": asset_path
        })
    
    @mcp.tool()
    async def get_asset_dependencies(asset_path: str) -> Dict:
        """Get all assets that the specified asset depends on.
        
        Args:
            asset_path: Full path to the asset
        
        Returns:
            Dictionary containing list of dependency assets
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("get_asset_dependencies", {
            "asset_path": asset_path
        })
    
    logger.info("Asset registry tools registered")