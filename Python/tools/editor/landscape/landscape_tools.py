"""
Landscape Tools for Unreal MCP.

This module provides tools for managing landscapes in Unreal Engine through the Landscape Editor module.
Following Epic's official structure: Editor/Landscape module patterns.
"""

import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_landscape_tools(mcp: FastMCP):
    """Register landscape tools with the MCP server."""
    
    @mcp.tool()
    def create_landscape(ctx: Context, 
                        size_x: int = 127, 
                        size_y: int = 127,
                        sections_per_component: int = 1,
                        quads_per_section: int = 63,
                        location_x: float = 0.0,
                        location_y: float = 0.0,
                        location_z: float = 0.0) -> Dict[str, Any]:
        """Create a landscape in the current level.
        
        Args:
            size_x: Landscape size in X direction (default: 127)
            size_y: Landscape size in Y direction (default: 127)
            sections_per_component: Number of sections per component (default: 1)
            quads_per_section: Number of quads per section (default: 63)
            location_x: X location of the landscape (default: 0.0)
            location_y: Y location of the landscape (default: 0.0)
            location_z: Z location of the landscape (default: 0.0)
            
        Returns:
            Dictionary containing the landscape creation result
            
        Example:
            create_landscape(size_x=255, size_y=255, location_z=100.0)
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("create_landscape", {
                "size_x": size_x,
                "size_y": size_y,
                "sections_per_component": sections_per_component,
                "quads_per_section": quads_per_section,
                "location": {
                    "x": location_x,
                    "y": location_y,
                    "z": location_z
                }
            })
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Created landscape with size {size_x}x{size_y}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating landscape: {e}")
            return {"error": f"Error creating landscape: {str(e)}"}
    
    @mcp.tool()
    def modify_landscape(ctx: Context, modification_type: str = "sculpt") -> Dict[str, Any]:
        """Modify the landscape heightmap.
        
        Args:
            modification_type: Type of modification to perform (default: "sculpt")
            
        Returns:
            Dictionary containing the landscape modification result
            
        Example:
            modify_landscape("sculpt")
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("modify_landscape", {
                "modification_type": modification_type
            })
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Modified landscape with type: {modification_type}")
            return response
            
        except Exception as e:
            logger.error(f"Error modifying landscape: {e}")
            return {"error": f"Error modifying landscape: {str(e)}"}
    
    @mcp.tool()
    def paint_landscape_layer(ctx: Context, layer_name: str) -> Dict[str, Any]:
        """Paint a landscape material layer.
        
        Args:
            layer_name: Name of the landscape layer to paint
            
        Returns:
            Dictionary containing the landscape painting result
            
        Example:
            paint_landscape_layer("Grass")
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("paint_landscape_layer", {
                "layer_name": layer_name
            })
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response from Unreal Engine"}
                
            logger.info(f"Painted landscape layer: {layer_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error painting landscape layer: {e}")
            return {"error": f"Error painting landscape layer: {str(e)}"}
    
    @mcp.tool()
    def get_landscape_info(ctx: Context) -> List[Dict[str, Any]]:
        """Get information about all landscapes in the current level.
        
        Returns:
            List of dictionaries containing landscape information
            
        Example:
            get_landscape_info()
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return []
                
            response = unreal.send_command("get_landscape_info", {})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return []
                
            # Check response format
            if "result" in response and "landscapes" in response["result"]:
                landscapes = response["result"]["landscapes"]
                logger.info(f"Found {len(landscapes)} landscapes in level")
                return landscapes
            elif "landscapes" in response:
                landscapes = response["landscapes"]
                logger.info(f"Found {len(landscapes)} landscapes in level")
                return landscapes
                
            logger.warning(f"Unexpected response format: {response}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting landscape info: {e}")
            return []