@echo off
echo ========================================
echo Rebuilding UnrealMCP Plugin
echo ========================================
echo.
echo This will rebuild the plugin with the screenshot fix.
echo Please ensure Unreal Editor is closed before continuing.
echo.
pause

REM Set the path to your Unreal Engine installation
set UE_PATH=C:\Program Files\Epic Games\UE_5.6

REM Generate project files
echo Generating project files...
"%UE_PATH%\Engine\Build\BatchFiles\GenerateProjectFiles.bat" "%~dp0MCPGameProject\MCPGameProject.uproject"

REM Build the project
echo.
echo Building plugin...
"%UE_PATH%\Engine\Build\BatchFiles\Build.bat" MCPGameProjectEditor Win64 Development "%~dp0MCPGameProject\MCPGameProject.uproject" -waitmutex

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo You can now:
echo 1. Open Unreal Editor with the MCPGameProject
echo 2. The screenshot functionality should now properly save to:
echo    - Relative paths: MCPGameProject/Saved/Screenshots/
echo    - Absolute paths: Exactly where specified
echo.
pause