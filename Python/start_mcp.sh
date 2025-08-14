#!/bin/bash
# Start the Unreal MCP server with proper environment settings
cd /mnt/c/Dev/UEFN/temp/unreal-mcp/Python
export UNREAL_HOST=192.168.1.106
export UNREAL_PORT=55557
exec uv run unreal_mcp_server.py