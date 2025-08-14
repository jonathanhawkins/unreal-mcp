#!/bin/bash
# Start the Unreal MCP server with proper environment settings

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Use environment variables if set, otherwise use defaults
# For WSL2 users: Set UNREAL_HOST to your Windows IP address
UNREAL_HOST="${UNREAL_HOST:-127.0.0.1}"
UNREAL_PORT="${UNREAL_PORT:-55557}"

export UNREAL_HOST
export UNREAL_PORT

echo "Starting Unreal MCP Server..."
echo "Connecting to Unreal at $UNREAL_HOST:$UNREAL_PORT"
exec uv run unreal_mcp_server.py