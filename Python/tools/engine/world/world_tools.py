"""
World Tools for Unreal MCP.

This module provides tools for runtime world operations in Unreal Engine.
Following Epic's official structure: Engine/World module patterns.
"""

import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_world_tools(mcp: FastMCP):
    """Register world runtime tools with the MCP server."""
    
    @mcp.tool()
    def get_current_level_info(ctx: Context) -> Dict[str, Any]:
        """Get information about the current level and world.
        
        Returns:
            Dictionary containing current world and level information
            
        Example:
            get_current_level_info()
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("get_current_level_info", {})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info("Retrieved current level info")
            return response
            
        except Exception as e:
            logger.error(f"Error getting level info: {e}")
            return {"error": f"Error getting level info: {str(e)}"}