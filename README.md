<div align="center">

# Model Context Protocol for Unreal Engine
<span style="color: #555555">unreal-mcp</span>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.5%2B-orange)](https://www.unrealengine.com)
[![Python](https://img.shields.io/badge/Python-3.12%2B-yellow)](https://www.python.org)
[![Status](https://img.shields.io/badge/Status-Experimental-red)](https://github.com/chongdashu/unreal-mcp)

</div>

This project enables AI assistant clients like Cursor, Windsurf and Claude Desktop to control Unreal Engine through natural language using the Model Context Protocol (MCP).

## ⚠️ Experimental Status

This project is currently in an **EXPERIMENTAL** state. The API, functionality, and implementation details are subject to significant changes. While we encourage testing and feedback, please be aware that:

- Breaking changes may occur without notice
- Features may be incomplete or unstable
- Documentation may be outdated or missing
- Production use is not recommended at this time

## 🌟 Overview

The Unreal MCP integration provides comprehensive tools for controlling Unreal Engine through natural language:

| Category | Capabilities |
|----------|-------------|
| **Actor Management** | • Create and delete actors (cubes, spheres, lights, cameras, etc.)<br>• Set actor transforms (position, rotation, scale)<br>• Query actor properties and find actors by name<br>• List all actors in the current level |
| **Blueprint Development** | • Create new Blueprint classes with custom components<br>• Add and configure components (mesh, camera, light, etc.)<br>• Set component properties and physics settings<br>• Compile Blueprints and spawn Blueprint actors<br>• Create input mappings for player controls |
| **Blueprint Node Graph** | • Add event nodes (BeginPlay, Tick, etc.)<br>• Create function call nodes and connect them<br>• Add variables with custom types and default values<br>• Create component and self references<br>• Find and manage nodes in the graph |
| **Editor Control** | • Focus viewport on specific actors or locations<br>• Control viewport camera orientation and distance<br>• Take screenshots of the viewport with configurable resolution |

All these capabilities are accessible through natural language commands via AI assistants, making it easy to automate and control Unreal Engine workflows.

## 🧩 Components

### Sample Project (MCPGameProject) `MCPGameProject`
- Based off the Blank Project, but with the UnrealMCP plugin added.

### Plugin (UnrealMCP) `MCPGameProject/Plugins/UnrealMCP`
- Native TCP server for MCP communication
- Integrates with Unreal Editor subsystems
- Implements actor manipulation tools
- Handles command execution and response handling

### Python MCP Server `Python/unreal_mcp_server.py`
- Implemented in `unreal_mcp_server.py`
- Manages TCP socket connections to the C++ plugin (port 55557)
- Handles command serialization and response parsing
- Provides error handling and connection management
- Loads and registers tool modules from the `tools` directory
- Uses the FastMCP library to implement the Model Context Protocol

## 📂 Directory Structure

- **MCPGameProject/** - Example Unreal project
  - **Plugins/UnrealMCP/** - C++ plugin source
    - **Source/UnrealMCP/** - Plugin source code
    - **UnrealMCP.uplugin** - Plugin definition

- **Python/** - Python server and tools
  - **tools/** - Tool modules for actor, editor, and blueprint operations
  - **scripts/** - Example scripts and demos

- **Docs/** - Comprehensive documentation
  - See [Docs/README.md](Docs/README.md) for documentation index

## 🚀 Quick Start Guide

### Prerequisites
- Unreal Engine 5.5+
- Python 3.12+
- MCP Client (e.g., Claude Desktop, Cursor, Windsurf)

### Sample project

For getting started quickly, feel free to use the starter project in `MCPGameProject`. This is a UE 5.5 Blank Starter Project with the `UnrealMCP.uplugin` already configured. 

1. **Prepare the project**
   - Right-click your .uproject file
   - Generate Visual Studio project files
2. **Build the project (including the plugin)**
   - Open solution (`.sln`)
   - Choose `Development Editor` as your target.
   - Build

### Starting Unreal Editor

#### Normal Start (Local connections only)
Simply open the project normally through Epic Games Launcher or by double-clicking the .uproject file.

#### For WSL2 or Remote Connections
You MUST start Unreal with special command-line arguments to allow external connections:

**PowerShell:**
```powershell
# Define paths (adjust to your installation)
$ue = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe"
$proj = "C:\Dev\UEFN\temp\unreal-mcp\MCPGameProject\MCPGameProject.uproject"

# Start with network binding to all interfaces
& "$ue" "$proj" -UnrealMCPBind="0.0.0.0" -UnrealMCPPort=55557
```

**Command Prompt:**
```cmd
"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe" "C:\Dev\UEFN\temp\unreal-mcp\MCPGameProject\MCPGameProject.uproject" -UnrealMCPBind=0.0.0.0 -UnrealMCPPort=55557
```

**Important Notes:**
- `-UnrealMCPBind=0.0.0.0` makes Unreal listen on all network interfaces (not just localhost)
- This is REQUIRED for WSL2 connections (WSL2 cannot access Windows localhost)
- Only use these flags if connecting from WSL2 or another machine
- Default port is 55557 (can be changed with `-UnrealMCPPort`)

### Plugin
Otherwise, if you want to use the plugin in your existing project:

1. **Copy the plugin to your project**
   - Copy `MCPGameProject/Plugins/UnrealMCP` to your project's Plugins folder

2. **Enable the plugin**
   - Edit > Plugins
   - Find "UnrealMCP" in Editor category
   - Enable the plugin
   - Restart editor when prompted

3. **Build the plugin**
   - Right-click your .uproject file
   - Generate Visual Studio project files
   - Open solution (`.sln)
   - Build with your target platform and output settings

### Python Server Setup

See [Python/README.md](Python/README.md) for detailed Python setup instructions, including:
- Setting up your Python environment
- Running the MCP server
- Using direct or server-based connections

### Configuring your MCP Client

#### Standard Configuration (Windows/Mac/Linux)
Use the following JSON for your mcp configuration:

```json
{
  "mcpServers": {
    "unrealMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "<path/to/the/folder/PYTHON>",
        "run",
        "unreal_mcp_server.py"
      ]
    }
  }
}
```

#### WSL2 Configuration
If running the MCP server in WSL2 while Unreal runs on Windows, you need to specify the Windows host IP:

```json
{
  "mcpServers": {
    "unrealMCP": {
      "command": "bash",
      "args": ["/path/to/unreal-mcp/Python/start_mcp.sh"],
      "env": {
        "UNREAL_HOST": "192.168.1.106",  // Replace with YOUR Windows IP
        "UNREAL_PORT": "55557"
      }
    }
  }
}
```

**To find your Windows IP for WSL2:**
1. From WSL2, run: `cat /etc/resolv.conf | grep nameserver`
2. Or use your Windows LAN IP: `ipconfig` (from Windows) and look for your IPv4 address

**Alternative WSL2 configuration using direct command:**
```json
{
  "mcpServers": {
    "unrealMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "/mnt/c/Dev/unreal-mcp/Python",  // WSL path format
        "run",
        "unreal_mcp_server.py"
      ],
      "env": {
        "UNREAL_HOST": "192.168.1.106",  // Your Windows IP
        "UNREAL_PORT": "55557"
      }
    }
  }
}
```

An example is found in `mcp.json`

### MCP Configuration Locations

Depending on which MCP client you're using, the configuration file location will differ:

| MCP Client | Configuration File Location | Notes |
|------------|------------------------------|-------|
| Claude Desktop | `~/.config/claude-desktop/mcp.json` | On Windows: `%USERPROFILE%\.config\claude-desktop\mcp.json` |
| Cursor | `.cursor/mcp.json` | Located in your project root directory |
| Windsurf | `~/.config/windsurf/mcp.json` | On Windows: `%USERPROFILE%\.config\windsurf\mcp.json` |

Each client uses the same JSON format as shown in the example above. 
Simply place the configuration in the appropriate location for your MCP client.


## Example MCP Usage

Once configured, you can use natural language commands in your MCP client:

### Creating Actors with Meshes
```
"Create a cube at position 0,0,100"
"Spawn a sphere at 200,0,100" 
"Add a cylinder mesh actor"
```
The actors will now appear with proper meshes (previously they were invisible).

### Taking Screenshots
```
"Take a screenshot of the viewport"
"Capture the current scene"
"Take a high-res screenshot at 4K resolution"
```
Screenshots are saved to the Unreal project's Screenshots folder.

### Blueprint Creation
```
"Create a new Blueprint called MyCharacter"
"Add a static mesh component to the Blueprint"
"Set the mesh to a cube"
```

## License
MIT

## Questions

For questions, you can reach me on X/Twitter: [@chongdashu](https://www.x.com/chongdashu)