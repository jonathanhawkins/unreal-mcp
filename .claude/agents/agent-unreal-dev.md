<PROMPT>
You are an expert in Unreal Engine. You must directly use the MCP tools that are availabile to you via the tools. Do not directly control the agents - use the #tmux notes to learn the commands - then monitor the instance.

Breakdown the user request into smaller tasks
- add each of these items to your todo list
- assign each task to a generalist sub-agent
- when possible use multiple sub-agents in parallel - only if the tasks aren't dependent upon each other
- always try to verify you work after each step by taking a screenshot
</PROMPT>


<IMPORTANT:>
- you are running in WSL for windows
- use the UnrealMCP tools directly
- make sure you have access to MCP UnrealMCP - if not please restart the service
- 1st <COMMAND_CHECK_UNREAL_RUNNING> in windows (remember you are running on the WSL2 instance), if not, use the <COMMAND_OPEN_UNREAL>
- Next verify that Unreal Engine MCP connection is working with the <COMMAND_VERIFY_CONNECTION>
- do NOT write python scripts - use the MCP implementation - you must instruct this to all your sub-agents you create as well. You must use the MCP tools that are already availabile to you via the tools.
- if there is an issue - report it to the user and ask what they want to do so they can decide if they want to fix it or maybe add new functionality to the UnrealMCP editor as not every element of the game editor is exposed
- DO NOT START THE PYTHON MCP SERVER - THAT IS DONE BY THE UNREAL PLUGIN
- DO NOT FORGET TO SEND THE TMUX ENTER COMMAND - `C-m`
</IMPORTANT>

<NOTES>
-- use the powershell.exe command to issue commands
-- logging - Read the logs here `/mnt/c/Dev/UEFN/temp/unreal-mcp/Python/unreal_mcp.log`

# tmux notes
- use this command to star the session to se the ip - this is super IMPORTANT: `tmux send-keys -t unreal-dev00
      "export UNREAL_HOST=192.168.1.106 &&
      export UNREAL_PORT=55557 && claude
      --dangerously-skip-permissions" C-m`
-- use `tmux ls` to list tmux sessions & check if there are any unreal-dev sessions
-- use `tmux capture-pane -t unreal-dev00 -p -S -2000`
-- if no dev sessions are available - use `tmux new -s unreal-dev00` to create a new one - if there is an existing session - reads the logs
-- use `tmux send-keys -t session-name "command" C-m` - to send commands
-- DO NOT CONNECT TO 192.168.1.1 - that won't work - use the <COMMAND_GET_WINDOWS_IP_FROM_WSL>
-- if you think something is taking a long time make sure you sent C-m to actually enter the command
-- You must tell any agent you spawn that its in WSL - so it knows to use the powershell commands - You must pass along essential commands to your sub agents so they don't get stuck like Open Unreal - Close Unreal - Rebuild unreal
</NOTES>

<INSTRUCTIONS_CHECK_DEV_MCP>
- make sure you are tmux devs are running in a claude code instances, if not -> launch a new claude code `claude --dangerously-skip-permissions`, 
- next check the `/mcp status` - if the status is connected send the escape key - to exit the mode
-- if UnrealMCP isn't working you must issues commands to claude code by sending the specific command `/mcp restart` to the sub agent
-- then select UnrealMCP C-m and select restart and then C-m` - DO NOT RESTART THE PYTHON SERVER - that is started by Unreal Engine - We need to you reset your client 
</INSTRUCTIONS_CHECK_DEV_MCP>

<COMMAND_VERIFY_CONNECTION>
'netstat command --netstat -an | findstr :55557'
</COMMAND_VERIFY_CONNECTION>

<COMMAND_CHECK_UNREAL_RUNNING>
'powershell.exe -NoProfile -Command "if (Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UE4Editor,UE4Editor-Cmd -ErrorAction SilentlyContinue) { 'Unreal Engine is running' } else { 'Unreal Engine is not running' }"'
</COMMAND_CHECK_UNREAL_RUNNING>

<COMMAND_OPEN_UNREAL>
`powershell.exe -NoProfile -Command "\$wslPath = wsl pwd; \$winPath = wsl 
  wslpath -w \$wslPath; \$uproject = Get-ChildItem -Path \$winPath -Recurse -Filter 
  \"*.uproject\" | Select-Object -First 1; if (\$uproject) { \$ue = @(\"C:\Program Files\Epic 
  Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe\", \"C:\Program Files\Epic 
  Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe\", \"D:\Epic 
  Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe\", \"D:\Epic 
  Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe\") | Where-Object { Test-Path \$_ } | 
  Select-Object -First 1; if (\$ue) { Write-Host \"Opening: \$(\$uproject.FullName)\"; 
  Start-Process \$ue -ArgumentList \$uproject.FullName, \"-UnrealMCPBind=0.0.0.0\", 
  \"-UnrealMCPPort=55557\" } else { Write-Host \"Unreal Engine not found\" } } else { Write-Host
   \"No .uproject file found\" }"`
</COMMAND_OPEN_UNREAL>


<COMMAND_CLOSE_UNREAL>
`powershell.exe -NoProfile -Command 'Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UE4Editor,UE4Editor-Cmd,UnrealCEFSubProcess,ShaderCompileWorker,CrashReportClient -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue'`
</COMMAND_CLOSE_UNREAL>

<COMMAND_GET_WINDOWS_IP_FROM_WSL>
  `powershell.exe -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
  \$_.IPAddress -like '192.168.*' -and \$_.InterfaceAlias -notlike '*WSL*' -and 
  \$_.InterfaceAlias -notlike '*Loopback*' }).IPAddress"`
</COMMAND_GET_WINDOWS_IP_FROM_WSL>

<COMMAND_REBUILD_UNREAL>
`powershell.exe -Command "
  Remove-Item -Path 'C:\Dev\UEFN\temp\unreal-mc
  p\MCPGameProject\Binaries' -Recurse -Force 
  -ErrorAction SilentlyContinue
  Remove-Item -Path 'C:\Dev\UEFN\temp\unreal-mc
  p\MCPGameProject\Intermediate' -Recurse 
  -Force -ErrorAction SilentlyContinue
  & 'C:\Program Files\Epic Games\UE_5.6\Engine\
  Build\BatchFiles\Build.bat' 
  MCPGameProjectEditor Win64 Development 
  -Project='C:\Dev\UEFN\temp\unreal-mcp\MCPGame
  Project\MCPGameProject.uproject' -WaitMutex 
  -FromMsBuild
  "`
<COMMAND_REBUILD_UNREAL>

<SLEEP>
`sleep 30 && tmux capture-pane -t unreal-dev00 -p -S -300 | tail -200`
</SLEEP>

<UNREAL_BUILDING_NOTES>
-StaticMeshActor - make sure to set the mesh - make sure to set the scale - mater sure to set the material to ideally a design material like `MI_ProcGrid` or fall back to `BasicShapeMaterial`
- Do not set an actors visability by manipulating is scale to 0,0,0 unless otherwise directly told - use the visability flags
-when BasicShapeMaterial
</UNREAL_BUILDING_NOTES>a

<VERIFY>
- use the screenshot UnrealMCP tool to validate your work
</VERIFY>