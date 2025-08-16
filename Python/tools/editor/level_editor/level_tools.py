"""
Level Editor Tools for Unreal MCP.

This module provides tools for managing levels in Unreal Engine through the Level Editor module.
Following Epic's official structure: Editor/LevelEditor module patterns.
"""

import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_level_tools(mcp: FastMCP):
    """Register level editor tools with the MCP server."""
    
    @mcp.tool()
    def create_level(ctx: Context, level_name: str) -> Dict[str, Any]:
        """Create a new level.
        
        Args:
            level_name: Name of the new level to create
            
        Returns:
            Dictionary containing the created level information
            
        Example:
            create_level("MyNewLevel")
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("create_level", {"level_name": level_name})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Created level: {level_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating level: {e}")
            return {"error": f"Error creating level: {str(e)}"}
    
    @mcp.tool()
    def save_level(ctx: Context) -> Dict[str, Any]:
        """Save the current level.
        
        Returns:
            Dictionary containing the save operation result
            
        Example:
            save_level()
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("save_level", {})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info("Level saved successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error saving level: {e}")
            return {"error": f"Error saving level: {str(e)}"}
    
    @mcp.tool()
    def load_level(ctx: Context, level_path: str) -> Dict[str, Any]:
        """Load a level.
        
        Args:
            level_path: Path to the level to load (e.g., "/Game/Maps/MyLevel")
            
        Returns:
            Dictionary containing the load operation result
            
        Example:
            load_level("/Game/Maps/MyLevel")
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("load_level", {"level_path": level_path})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Loaded level: {level_path}")
            return response
            
        except Exception as e:
            logger.error(f"Error loading level: {e}")
            return {"error": f"Error loading level: {str(e)}"}
    
    @mcp.tool()
    def set_level_visibility(ctx: Context, level_name: str, visible: bool = True) -> Dict[str, Any]:
        """Set the visibility of a level.
        
        Args:
            level_name: Name of the level to set visibility for
            visible: Whether the level should be visible (default: True)
            
        Returns:
            Dictionary containing the visibility operation result
            
        Example:
            set_level_visibility("MyLevel", True)
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("set_level_visibility", {
                "level_name": level_name,
                "visible": visible
            })
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Set level {level_name} visibility to {visible}")
            return response
            
        except Exception as e:
            logger.error(f"Error setting level visibility: {e}")
            return {"error": f"Error setting level visibility: {str(e)}"}
    
    @mcp.tool()
    def create_streaming_level(ctx: Context, level_path: str) -> Dict[str, Any]:
        """Create a streaming level.
        
        Args:
            level_path: Path to the level to add as streaming level
            
        Returns:
            Dictionary containing the streaming level creation result
            
        Example:
            create_streaming_level("/Game/Maps/StreamingLevel")
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("create_streaming_level", {"level_path": level_path})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Created streaming level: {level_path}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating streaming level: {e}")
            return {"error": f"Error creating streaming level: {str(e)}"}
    
    @mcp.tool()
    def load_streaming_level(ctx: Context, level_name: str) -> Dict[str, Any]:
        """Load a streaming level.
        
        Args:
            level_name: Name of the streaming level to load
            
        Returns:
            Dictionary containing the streaming level load result
            
        Example:
            load_streaming_level("StreamingLevel")
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("load_streaming_level", {"level_name": level_name})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Loaded streaming level: {level_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error loading streaming level: {e}")
            return {"error": f"Error loading streaming level: {str(e)}"}
    
    @mcp.tool()
    def unload_streaming_level(ctx: Context, level_name: str) -> Dict[str, Any]:
        """Unload a streaming level.
        
        Args:
            level_name: Name of the streaming level to unload
            
        Returns:
            Dictionary containing the streaming level unload result
            
        Example:
            unload_streaming_level("StreamingLevel")
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("unload_streaming_level", {"level_name": level_name})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Unloaded streaming level: {level_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error unloading streaming level: {e}")
            return {"error": f"Error unloading streaming level: {str(e)}"}