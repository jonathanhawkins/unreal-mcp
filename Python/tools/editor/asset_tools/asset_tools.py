"""Core asset management tools for Unreal Engine via MCP."""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

def register_tools(mcp, connection=None):
    """Register core asset tools with the MCP server."""
    
    # Import get_unreal_connection from parent module
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    from unreal_mcp_server import get_unreal_connection
    
    @mcp.tool()
    async def load_asset(asset_path: str) -> Dict:
        """Load an asset into memory.
        
        Args:
            asset_path: Full path to the asset to load
        
        Returns:
            Dictionary with load status and asset information
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("load_asset", {
            "asset_path": asset_path
        })
    
    @mcp.tool()
    async def save_asset(asset_path: str, only_if_dirty: bool = True) -> Dict:
        """Save an asset to disk.
        
        Args:
            asset_path: Full path to the asset to save
            only_if_dirty: Only save if the asset has unsaved changes
        
        Returns:
            Dictionary with save status
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("save_asset", {
            "asset_path": asset_path,
            "only_if_dirty": only_if_dirty
        })
    
    @mcp.tool()
    async def duplicate_asset(source_path: str, destination_path: str) -> Dict:
        """Duplicate an existing asset.
        
        Args:
            source_path: Path to the asset to duplicate
            destination_path: Path for the new duplicated asset
        
        Returns:
            Dictionary with duplication status
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("duplicate_asset", {
            "source_path": source_path,
            "destination_path": destination_path
        })
    
    @mcp.tool()
    async def delete_asset(asset_path: str) -> Dict:
        """Delete an asset from the project.
        
        Args:
            asset_path: Full path to the asset to delete
        
        Returns:
            Dictionary with deletion status
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("delete_asset", {
            "asset_path": asset_path
        })
    
    @mcp.tool()
    async def rename_asset(source_path: str, new_name: str) -> Dict:
        """Rename an existing asset.
        
        Args:
            source_path: Current path to the asset
            new_name: New name for the asset (without path)
        
        Returns:
            Dictionary with rename status and new path
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("rename_asset", {
            "source_path": source_path,
            "new_name": new_name
        })
    
    @mcp.tool()
    async def move_asset(source_path: str, destination_path: str) -> Dict:
        """Move an asset to a different location.
        
        Args:
            source_path: Current path to the asset
            destination_path: New full path for the asset
        
        Returns:
            Dictionary with move status
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("move_asset", {
            "source_path": source_path,
            "destination_path": destination_path
        })
    
    @mcp.tool()
    async def import_asset(file_path: str, destination_path: str) -> Dict:
        """Import an external file as an asset.
        
        Args:
            file_path: Path to the file on disk to import
            destination_path: Content browser path where to import the asset
        
        Returns:
            Dictionary with import status and imported asset information
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("import_asset", {
            "file_path": file_path,
            "destination_path": destination_path
        })
    
    @mcp.tool()
    async def export_asset(asset_path: str, export_path: str) -> Dict:
        """Export an asset to an external file.
        
        Args:
            asset_path: Full path to the asset to export
            export_path: File path where to export the asset
        
        Returns:
            Dictionary with export status
        """
        conn = get_unreal_connection()
        if not conn:
            return {"status": "error", "error": "Failed to connect to Unreal Engine"}
        return conn.send_command("export_asset", {
            "asset_path": asset_path,
            "export_path": export_path
        })
    
    logger.info("Core asset tools registered")