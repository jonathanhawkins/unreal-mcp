"""Content browser tools for Unreal Engine via MCP."""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

def register_tools(mcp, connection=None):
    """Register content browser tools with the MCP server."""
    
    # Import get_unreal_connection from parent module
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    from unreal_mcp_server import get_unreal_connection
    
    @mcp.tool()
    async def list_assets(path: str = "/Game", type_filter: str = "", recursive: bool = False) -> Dict:
        """List all assets in a given path.
        
        Args:
            path: The content browser path to list (e.g., "/Game/MyFolder")
            type_filter: Optional asset type filter (e.g., "StaticMesh", "Material")
            recursive: Whether to search recursively in subdirectories
        
        Returns:
            Dictionary containing list of assets and count
        """
        params = {
            "path": path,
            "recursive": recursive
        }
        if type_filter:
            params["type_filter"] = type_filter
        
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("list_assets", params)
    
    @mcp.tool()
    async def get_asset_metadata(asset_path: str) -> Dict:
        """Get detailed metadata for a specific asset.
        
        Args:
            asset_path: Full path to the asset (e.g., "/Game/MyFolder/MyAsset")
        
        Returns:
            Dictionary containing asset metadata including tags and properties
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("get_asset_metadata", {
            "asset_path": asset_path
        })
    
    @mcp.tool()
    async def search_assets(search_text: str, type_filter: str = "") -> Dict:
        """Search for assets by name or path.
        
        Args:
            search_text: Text to search for in asset names and paths
            type_filter: Optional asset type filter
        
        Returns:
            Dictionary containing matching assets
        """
        params = {"search_text": search_text}
        if type_filter:
            params["type_filter"] = type_filter
        
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("search_assets", params)
    
    logger.info("Content browser tools registered")