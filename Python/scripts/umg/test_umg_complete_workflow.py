#!/usr/bin/env python3
"""
Complete UMG Widget workflow test for UnrealMCP.

This script demonstrates the full UMG workflow using actual MCP tools
when Unreal Engine is running with the UnrealMCP plugin.

Usage:
    python scripts/umg/test_umg_complete_workflow.py

Requirements:
    - Unreal Engine 5.6+ running with UnrealMCP plugin
    - UnrealMCP TCP server listening on port 55557
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to sys.path to import unreal_mcp_server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unreal_mcp_server import get_unreal_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UMG_Test")


async def test_complete_umg_workflow():
    """Test complete UMG workflow with real Unreal Engine connection."""
    
    logger.info("Testing complete UMG workflow...")
    
    # Get connection to Unreal Engine
    unreal = get_unreal_connection()
    if not unreal:
        logger.error("❌ Cannot connect to Unreal Engine")
        logger.info("Make sure Unreal Engine is running with UnrealMCP plugin loaded")
        return False
    
    logger.info("✅ Connected to Unreal Engine")
    
    try:
        # Step 1: Create a new UMG Widget Blueprint
        logger.info("Step 1: Creating UMG Widget Blueprint...")
        create_response = await unreal.send_command("create_umg_widget_blueprint", {
            "widget_name": "WBP_TestMainMenu",
            "parent_class": "UserWidget",
            "path": "/Game/Test/UI"
        })
        
        if not create_response.get("success"):
            logger.error(f"❌ Failed to create widget: {create_response}")
            return False
            
        logger.info("✅ Created WBP_TestMainMenu widget blueprint")
        widget_path = create_response.get("widget_path", "/Game/Test/UI/WBP_TestMainMenu")
        
        # Step 2: Add title text block
        logger.info("Step 2: Adding title text block...")
        title_response = await unreal.send_command("add_text_block_to_widget", {
            "widget_name": "WBP_TestMainMenu",
            "text_block_name": "TitleText",
            "text": "Main Menu",
            "position": [400, 100],
            "size": [300, 60],
            "font_size": 24,
            "color": [1.0, 1.0, 1.0, 1.0]
        })
        
        if not title_response.get("success"):
            logger.error(f"❌ Failed to add title text: {title_response}")
            return False
            
        logger.info("✅ Added title text block")
        
        # Step 3: Add subtitle text block
        logger.info("Step 3: Adding subtitle text block...")
        subtitle_response = await unreal.send_command("add_text_block_to_widget", {
            "widget_name": "WBP_TestMainMenu",
            "text_block_name": "SubtitleText",
            "text": "Choose an option below",
            "position": [350, 180],
            "size": [400, 30],
            "font_size": 16,
            "color": [0.8, 0.8, 0.8, 1.0]
        })
        
        if not subtitle_response.get("success"):
            logger.error(f"❌ Failed to add subtitle text: {subtitle_response}")
            return False
            
        logger.info("✅ Added subtitle text block")
        
        # Step 4: Add Start Game button
        logger.info("Step 4: Adding Start Game button...")
        start_button_response = await unreal.send_command("add_button_to_widget", {
            "widget_name": "WBP_TestMainMenu",
            "button_name": "StartGameButton",
            "text": "Start Game",
            "position": [375, 250],
            "size": [150, 45],
            "font_size": 14,
            "color": [1.0, 1.0, 1.0, 1.0],
            "background_color": [0.2, 0.6, 0.2, 1.0]
        })
        
        if not start_button_response.get("success"):
            logger.error(f"❌ Failed to add start button: {start_button_response}")
            return False
            
        logger.info("✅ Added Start Game button")
        
        # Step 5: Add Options button
        logger.info("Step 5: Adding Options button...")
        options_button_response = await unreal.send_command("add_button_to_widget", {
            "widget_name": "WBP_TestMainMenu",
            "button_name": "OptionsButton",
            "text": "Options",
            "position": [375, 310],
            "size": [150, 45],
            "font_size": 14,
            "color": [1.0, 1.0, 1.0, 1.0],
            "background_color": [0.2, 0.2, 0.6, 1.0]
        })
        
        if not options_button_response.get("success"):
            logger.error(f"❌ Failed to add options button: {options_button_response}")
            return False
            
        logger.info("✅ Added Options button")
        
        # Step 6: Add Exit button
        logger.info("Step 6: Adding Exit button...")
        exit_button_response = await unreal.send_command("add_button_to_widget", {
            "widget_name": "WBP_TestMainMenu",
            "button_name": "ExitButton", 
            "text": "Exit",
            "position": [375, 370],
            "size": [150, 45],
            "font_size": 14,
            "color": [1.0, 1.0, 1.0, 1.0],
            "background_color": [0.6, 0.2, 0.2, 1.0]
        })
        
        if not exit_button_response.get("success"):
            logger.error(f"❌ Failed to add exit button: {exit_button_response}")
            return False
            
        logger.info("✅ Added Exit button")
        
        # Step 7: Bind button events
        logger.info("Step 7: Binding button events...")
        
        buttons_to_bind = [
            ("StartGameButton", "OnStartGameClicked"),
            ("OptionsButton", "OnOptionsClicked"),
            ("ExitButton", "OnExitClicked")
        ]
        
        for button_name, function_name in buttons_to_bind:
            bind_response = await unreal.send_command("bind_widget_event", {
                "widget_name": "WBP_TestMainMenu",
                "widget_component_name": button_name,
                "event_name": "OnClicked",
                "function_name": function_name
            })
            
            if not bind_response.get("success"):
                logger.error(f"❌ Failed to bind {button_name} event: {bind_response}")
                return False
                
            logger.info(f"✅ Bound {button_name}.OnClicked to {function_name}")
        
        # Step 8: Add status text with property binding
        logger.info("Step 8: Adding status text with property binding...")
        status_response = await unreal.send_command("add_text_block_to_widget", {
            "widget_name": "WBP_TestMainMenu",
            "text_block_name": "StatusText",
            "text": "Ready",
            "position": [50, 450],
            "size": [200, 25],
            "font_size": 12,
            "color": [0.0, 1.0, 0.0, 1.0]
        })
        
        if not status_response.get("success"):
            logger.error(f"❌ Failed to add status text: {status_response}")
            return False
            
        logger.info("✅ Added status text block")
        
        # Step 9: Set up property bindings
        logger.info("Step 9: Setting up property bindings...")
        
        bindings_to_create = [
            ("StatusText", "CurrentStatus"),
            ("TitleText", "GameTitle")
        ]
        
        for text_block_name, property_name in bindings_to_create:
            binding_response = await unreal.send_command("set_text_block_binding", {
                "widget_name": "WBP_TestMainMenu",
                "text_block_name": text_block_name,
                "binding_property": property_name,
                "binding_type": "Text"
            })
            
            if not binding_response.get("success"):
                logger.error(f"❌ Failed to bind {text_block_name} property: {binding_response}")
                return False
                
            logger.info(f"✅ Bound {text_block_name} to {property_name}")
        
        # Step 10: Add widget to viewport
        logger.info("Step 10: Adding widget to viewport...")
        viewport_response = await unreal.send_command("add_widget_to_viewport", {
            "widget_name": "WBP_TestMainMenu",
            "z_order": 0
        })
        
        if not viewport_response.get("success"):
            logger.error(f"❌ Failed to add widget to viewport: {viewport_response}")
            return False
            
        logger.info("✅ Added widget to viewport")
        instance_id = viewport_response.get("instance_id", "Unknown")
        logger.info(f"Widget instance ID: {instance_id}")
        
        # Step 11: Take screenshot for verification
        logger.info("Step 11: Taking screenshot for verification...")
        screenshot_response = await unreal.send_command("take_screenshot", {
            "filename": "umg_workflow_test",
            "show_ui": True
        })
        
        if not screenshot_response.get("success"):
            logger.error(f"❌ Failed to take screenshot: {screenshot_response}")
            return False
            
        logger.info("✅ Screenshot taken for verification")
        screenshot_path = screenshot_response.get("path", "Unknown")
        logger.info(f"Screenshot saved to: {screenshot_path}")
        
        # Final success
        logger.info("🎉 Complete UMG workflow test PASSED!")
        logger.info("=" * 50)
        logger.info("Created widget with:")
        logger.info("- Title and subtitle text blocks")
        logger.info("- Three styled buttons (Start Game, Options, Exit)")
        logger.info("- Event bindings for button interactions")
        logger.info("- Property bindings for dynamic text")
        logger.info("- Widget displayed in viewport")
        logger.info("- Screenshot verification")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        return False


async def main():
    """Main function."""
    success = await test_complete_umg_workflow()
    
    if success:
        logger.info("✅ UMG workflow test completed successfully")
        return 0
    else:
        logger.error("❌ UMG workflow test failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)