@echo off
REM StartUnrealWithMCP.bat - Start Unreal Editor with MCP network binding
REM This is required for WSL2 or remote connections

echo ========================================
echo Starting Unreal Editor with MCP Support
echo ========================================
echo.
echo This will start Unreal Engine with network binding enabled
echo to allow connections from WSL2 or remote machines.
echo.

REM Define paths - adjust these if your installation is different
set UE_PATH=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe
set PROJECT_PATH=C:\Dev\UEFN\temp\unreal-mcp\MCPGameProject\MCPGameProject.uproject

REM Check if Unreal Editor exists
if not exist "%UE_PATH%" (
    echo ERROR: Unreal Editor not found at: %UE_PATH%
    echo Please edit this batch file and update UE_PATH
    pause
    exit /b 1
)

REM Check if project exists
if not exist "%PROJECT_PATH%" (
    echo ERROR: Project not found at: %PROJECT_PATH%
    echo Please edit this batch file and update PROJECT_PATH
    pause
    exit /b 1
)

echo Starting Unreal Editor...
echo Path: %UE_PATH%
echo Project: %PROJECT_PATH%
echo.
echo Network Settings:
echo - Binding to: 0.0.0.0 (all interfaces)
echo - Port: 55557
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause > nul

REM Start Unreal with MCP network binding
"%UE_PATH%" "%PROJECT_PATH%" -UnrealMCPBind=0.0.0.0 -UnrealMCPPort=55557

echo.
echo Unreal Editor has closed.
pause