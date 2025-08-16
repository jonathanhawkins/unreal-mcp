# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Unreal Engine 5.6 project that implements the Model Context Protocol (MCP) for controlling Unreal Engine through natural language. It consists of:

1. **C++ Plugin** (`MCPGameProject/Plugins/UnrealMCP/`) - Native TCP server that integrates with Unreal Editor
2. **Python MCP Server** (`Python/`) - Bridges MCP clients to the C++ plugin via TCP port 55557
3. **Sample Project** (`MCPGameProject/`) - UE 5.6 project with the plugin pre-configured

## Coding Standards

This project follows the [Allar UE5 Style Guide](https://github.com/Allar/ue5-style-guide) for consistency and maintainability. Key standards documents:

- **Naming Conventions**: `.claude/agents/shared/ue5-naming-conventions.md`
- **Project Organization**: `.claude/agents/shared/project-organization.md`
- **Blueprint Standards**: `.claude/agents/shared/blueprint-standards.md`

All code, assets, and blueprints should follow these standards to maintain consistency across the project.

## Essential Commands

### Building the Project

#### First-time setup:
```bash
# From project root, generate Visual Studio project files
# Right-click MCPGameProject.uproject → Generate Visual Studio project files
# OR use UnrealBuildTool directly (adjust path to your UE installation)
"C:/Program Files/Epic Games/UE_5.6/Engine/Build/BatchFiles/GenerateProjectFiles.bat" MCPGameProject.uproject

# Open MCPGameProject.sln in Visual Studio
# Set configuration to "Development Editor" 
# Build solution (F7 or Build → Build Solution)
```

#### Python Server Setup:
```bash
cd Python
uv venv
source .venv/bin/activate  # Unix/macOS
# OR
.venv\Scripts\activate      # Windows

uv pip install -e .
```

#### Running the MCP Server:
```bash
cd Python
uv run unreal_mcp_server.py

# For WSL or remote connections:
uv run unreal_mcp_server.py --unreal_host "$(hostname).local" --unreal_port 55557
```

### Testing Scripts

Run example scripts to test functionality:
```bash
cd Python
python scripts/actors/test_cube.py
python scripts/blueprints/test_create_and_spawn_cube_blueprint.py
python scripts/node/test_input_mapping.py
```

## Architecture Overview

### Communication Flow
```
MCP Client (Cursor/Claude) ← stdio → Python MCP Server ← TCP:55557 → Unreal C++ Plugin
```

### C++ Plugin Structure
- **UnrealMCPBridge** (`UnrealMCPBridge.h/cpp`) - Main editor subsystem managing TCP server
- **MCPServerRunnable** (`MCPServerRunnable.h/cpp`) - Handles TCP socket connections and JSON command routing
- **Command Handlers** - Modular command processors:
  - `UnrealMCPEditorCommands` - Editor and actor manipulation
  - `UnrealMCPBlueprintCommands` - Blueprint creation and compilation
  - `UnrealMCPBlueprintNodeCommands` - Blueprint node graph manipulation
  - `UnrealMCPProjectCommands` - Project-level operations
  - `UnrealMCPUMGCommands` - UI/Widget operations

### Python Server Components
- **unreal_mcp_server.py** - FastMCP server handling stdio transport
- **UnrealConnection** class - Manages TCP socket to C++ plugin with retry logic
- **Tool Modules** (`tools/`) - MCP tool definitions for different Unreal subsystems
  - `blueprint_tools.py` - Blueprint operations
  - `editor_tools.py` - Actor and viewport control
  - `node_tools.py` - Blueprint node operations
  - `project_tools.py` - Project operations
  - `umg_tools.py` - UI/UMG operations

### Command Protocol
Commands are JSON objects with structure:
```json
{
  "command": "command_name",
  "params": { /* command-specific parameters */ }
}
```

Response format:
```json
{
  "success": true/false,
  "result": /* command result */,
  "error": "error message if failed"
}
```

## Important Conventions

### Unreal Engine Specifics
- **Coordinate System**: Z-up, left-handed
  - X: Forward (Red)
  - Y: Right (Green)  
  - Z: Up (Blue)
- **Units**: Centimeters for distance, degrees for angles
- **Engine Version**: 5.6 - avoid deprecated APIs

### Python MCP Tools
- No `Optional`, `Union`, or `Any` types in `@mcp.tool()` decorated functions
- Handle defaults in method body, not type hints
- Always include docstrings with input examples

### Network Configuration
- Default bind: `127.0.0.1:55557`
- Override via environment or command line:
  ```bash
  # Environment variables
  UNREAL_MCP_BIND=0.0.0.0 UNREAL_MCP_PORT=55557 UnrealEditor.exe
  
  # Command line flags
  UnrealEditor.exe -UnrealMCPBind=0.0.0.0 -UnrealMCPPort=55557
  ```

### Connection Timeouts
Configurable via environment variables:
- `UNREAL_MCP_CONN_TIMEOUT` (default: 10s)
- `UNREAL_MCP_RECV_TIMEOUT` (default: 30s)

## Common Development Tasks

### Adding New Commands

1. **C++ Side** - Add handler in appropriate command class:
```cpp
// In UnrealMCPEditorCommands.cpp
if (CommandType == TEXT("new_command"))
{
    // Implementation
    return FString::Printf(TEXT("{\"success\":true,\"result\":\"%s\"}"), *Result);
}
```

2. **Python Side** - Add MCP tool in appropriate module:
```python
# In tools/editor_tools.py
@mcp.tool()
def new_command(param: str) -> str:
    """Tool description."""
    return await connection.send_command("new_command", {"param": param})
```

### Debugging

- Check logs: `Python/unreal_mcp.log`
- Enable stderr logging: `UNREAL_MCP_LOG_STDERR=1`
- Unreal logs: `MCPGameProject/Saved/Logs/`

## Key Files to Know

- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/UnrealMCPBridge.cpp` - Main plugin logic
- `Python/unreal_mcp_server.py` - MCP server entry point
- `Python/tools/` - All MCP tool implementations
- `.clinerules` and `.cursor/rules/unreal.mdc` - Important conventions for Unreal development

## New Modular Architecture (Phase 1)

### Asset Management
- **C++**: `Commands/Assets/UnrealMCPAssetCommands.h/cpp` - Asset operations (list, load, save, duplicate, delete, rename, import, export, references, dependencies)
- **Python**: `tools/assets/asset_tools.py` - MCP tools for asset management
- **Test**: `scripts/assets/test_asset_management.py` - Asset management testing

### World/Level Management  
- **C++**: `Commands/World/UnrealMCPWorldCommands.h/cpp` - Level and landscape operations
- **Python**: `tools/world/level_tools.py`, `tools/world/landscape_tools.py` - World/level MCP tools
- **Test**: `scripts/world/test_level_management.py` - Level management testing

### Available Commands

#### Asset Commands
- `list_assets` - List assets in directory with optional filtering
- `get_asset_metadata` - Get detailed asset information
- `search_assets` - Search assets by name/path
- `load_asset`, `save_asset` - Asset loading/saving
- `duplicate_asset`, `delete_asset`, `rename_asset`, `move_asset` - Asset operations
- `import_asset`, `export_asset` - Asset import/export
- `get_asset_references`, `get_asset_dependencies` - Asset relationship analysis

#### World/Level Commands
- `create_level`, `save_level`, `load_level` - Level management
- `get_current_level_info` - World/level information
- `set_level_visibility` - Level visibility control
- `create_landscape`, `modify_landscape`, `paint_landscape_layer`, `get_landscape_info` - Landscape operations
- `create_streaming_level`, `load_streaming_level`, `unload_streaming_level` - Streaming level management