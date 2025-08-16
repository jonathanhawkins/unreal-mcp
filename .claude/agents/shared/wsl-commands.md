# WSL/Windows Commands Reference

This document contains all essential commands for controlling Unreal Engine from WSL2 environment.

## Environment Setup

Before using these commands, set up your environment variables. Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# Set these to match your project location
export PROJECT_ROOT="/path/to/your/unreal-mcp"  # WSL path to your project
export WIN_PROJECT_ROOT="C:\\path\\to\\your\\unreal-mcp"  # Windows path to your project

# Example:
# export PROJECT_ROOT="/mnt/c/Dev/UEFN/temp/unreal-mcp"
# export WIN_PROJECT_ROOT="C:\\Dev\\UEFN\\temp\\unreal-mcp"
```

Reload your shell or run `source ~/.bashrc` after making changes.

## Environment Detection

### Check if Running in WSL
```bash
if grep -qi microsoft /proc/version; then
    echo "Running in WSL"
else
    echo "Not running in WSL"
fi
```

## Unreal Engine Control

### Check if Unreal is Running
```bash
powershell.exe -NoProfile -Command "if (Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UE4Editor,UE4Editor-Cmd -ErrorAction SilentlyContinue) { 'Unreal Engine is running' } else { 'Unreal Engine is not running' }"
```

### Open Unreal Engine with MCP
```bash
powershell.exe -NoProfile -Command "\$wslPath = wsl pwd; \$winPath = wsl wslpath -w \$wslPath; \$uproject = Get-ChildItem -Path \$winPath -Recurse -Filter \"*.uproject\" | Select-Object -First 1; if (\$uproject) { \$ue = @(\"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe\", \"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe\", \"D:\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe\", \"D:\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe\") | Where-Object { Test-Path \$_ } | Select-Object -First 1; if (\$ue) { Write-Host \"Opening: \$(\$uproject.FullName)\"; Start-Process \$ue -ArgumentList \$uproject.FullName, \"-UnrealMCPBind=0.0.0.0\", \"-UnrealMCPPort=55557\" } else { Write-Host \"Unreal Engine not found\" } } else { Write-Host \"No .uproject file found\" }"
```

### Close Unreal Engine
```bash
powershell.exe -NoProfile -Command 'Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UE4Editor,UE4Editor-Cmd,UnrealCEFSubProcess,ShaderCompileWorker,CrashReportClient -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue'
```

### Rebuild Unreal Project
```bash
powershell.exe -Command "
  Remove-Item -Path '${WIN_PROJECT_ROOT}\MCPGameProject\Binaries' -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item -Path '${WIN_PROJECT_ROOT}\MCPGameProject\Intermediate' -Recurse -Force -ErrorAction SilentlyContinue
  & 'C:\Program Files\Epic Games\UE_5.6\Engine\Build\BatchFiles\Build.bat' MCPGameProjectEditor Win64 Development -Project='${WIN_PROJECT_ROOT}\MCPGameProject\MCPGameProject.uproject' -WaitMutex -FromMsBuild
"
```

## Network Configuration

### Get Windows IP from WSL
```bash
powershell.exe -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { \$_.IPAddress -like '192.168.*' -and \$_.InterfaceAlias -notlike '*WSL*' -and \$_.InterfaceAlias -notlike '*Loopback*' }).IPAddress"
```

### Verify MCP Connection
```bash
netstat -an | grep :55557
```

### Check MCP Port from Windows Side
```bash
powershell.exe -NoProfile -Command "netstat -an | findstr :55557"
```

## Path Conversion

### Convert WSL Path to Windows Path
```bash
wslpath -w "${PROJECT_ROOT}"
# Example output: C:\Dev\UEFN\temp\unreal-mcp
```

### Convert Windows Path to WSL Path
```bash
wslpath -u "${WIN_PROJECT_ROOT}"
# Example output: /mnt/c/Dev/UEFN/temp/unreal-mcp
```

## Tmux Session Management

### Create New Session
```bash
tmux new -s unreal-dev00
```

### Send Commands to Session
```bash
tmux send-keys -t unreal-dev00 "command here" C-m
```

### Capture Session Output
```bash
tmux capture-pane -t unreal-dev00 -p -S -2000
```

### List Active Sessions
```bash
tmux ls
```

### Kill Session
```bash
tmux kill-session -t unreal-dev00
```

## Spawning Claude Agents

### Spawn Research Agent
```bash
tmux new -s unreal-research00
tmux send-keys -t unreal-research00 "claude --dangerously-skip-permissions" C-m
```

### Spawn Development Agent with Environment
```bash
tmux new -s unreal-dev00
tmux send-keys -t unreal-dev00 "export UNREAL_HOST=$(powershell.exe -NoProfile -Command \"(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { \\\$_.IPAddress -like '192.168.*' -and \\\$_.InterfaceAlias -notlike '*WSL*' -and \\\$_.InterfaceAlias -notlike '*Loopback*' }).IPAddress\" | tr -d '\r\n') && export UNREAL_PORT=55557 && claude --dangerously-skip-permissions" C-m
```

## MCP Service Management

### Check MCP Status (in Claude session)
```
/mcp status
```

### Restart MCP Service (in Claude session)
```
/mcp restart
# Then select UnrealMCP from the list
```

## Logging and Debugging

### View MCP Logs
```bash
tail -f "${PROJECT_ROOT}/Python/unreal_mcp.log"
```

### Check Unreal Logs
```bash
ls -la "${PROJECT_ROOT}/MCPGameProject/Saved/Logs/"
```

### Monitor Windows Processes
```bash
powershell.exe -Command "Get-Process | Where-Object {$_.Name -like '*Unreal*'}"
```

## Important Notes

1. **Always escape $ in PowerShell commands** when passing through bash
2. **Use tr -d '\r\n'** to clean Windows line endings from PowerShell output
3. **Always send C-m** after tmux send-keys to execute the command
4. **Never connect to 192.168.1.1** - use the actual Windows IP
5. **MCP Port 55557** must be bound to 0.0.0.0 for WSL access

## Sleep and Wait

### Wait and Check Output
```bash
sleep 30 && tmux capture-pane -t unreal-dev00 -p -S -300 | tail -200
```

## Common Issues and Solutions

### Issue: Can't connect to MCP from WSL
Solution: Ensure Unreal was started with `-UnrealMCPBind=0.0.0.0`

### Issue: PowerShell commands fail
Solution: Check quotes and escape characters, especially for $

### Issue: Tmux command doesn't execute
Solution: Ensure you're sending C-m at the end

### Issue: Can't find Windows IP
Solution: Use the full PowerShell command with proper filters