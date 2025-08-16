# MCP (Model Context Protocol) Usage Guidelines

## Environment Setup

For path references in this document, ensure you have these environment variables set:

```bash
# Set in your ~/.bashrc or ~/.zshrc
export PROJECT_ROOT="/path/to/your/unreal-mcp"  # WSL path to your project
export WIN_PROJECT_ROOT="C:\\path\\to\\your\\unreal-mcp"  # Windows path to your project
```

## Critical Rules

### DO NOT:
- ❌ **NEVER write Python scripts** to interact with Unreal
- ❌ **NEVER start the Python MCP server manually** (Unreal plugin handles this)
- ❌ **NEVER bypass MCP tools** to control Unreal
- ❌ **NEVER assume MCP is connected** without checking

### ALWAYS:
- ✅ **Use MCP tools directly** via the tool interface
- ✅ **Check MCP status** before starting work
- ✅ **Verify connection** to UnrealMCP service
- ✅ **Use provided MCP tools** for all Unreal operations

## MCP Service Management

### Check MCP Status
In any Claude session:
```
/mcp status
```

Look for `UnrealMCP` in the list. It should show as connected.

### Restart MCP Service
If UnrealMCP is not working:
```
/mcp restart
```
Then select `UnrealMCP` from the list and restart it.

## Available MCP Tools

### Actor Management
- `get_actors_in_level` - List all actors in current level
- `find_actors_by_name` - Search actors by name pattern
- `spawn_actor` - Create new actor in level
- `delete_actor` - Remove actor from level
- `set_actor_transform` - Move/rotate/scale actor
- `get_actor_properties` - Get all actor properties
- `set_actor_property` - Set specific actor property
- `spawn_blueprint_actor` - Spawn actor from Blueprint

### Blueprint Operations
- `create_blueprint` - Create new Blueprint class
- `add_component_to_blueprint` - Add components to Blueprint
- `set_static_mesh_properties` - Configure static mesh components
- `set_component_property` - Set component properties
- `set_physics_properties` - Configure physics on components
- `compile_blueprint` - Compile Blueprint after changes
- `set_blueprint_property` - Set Blueprint default properties

### Blueprint Node Graph
- `add_blueprint_event_node` - Add event nodes (BeginPlay, Tick, etc.)
- `add_blueprint_input_action_node` - Add input action events
- `add_blueprint_function_node` - Add function call nodes
- `connect_blueprint_nodes` - Connect nodes in graph
- `add_blueprint_variable` - Add variables to Blueprint
- `add_blueprint_get_self_component_reference` - Get component references
- `add_blueprint_self_reference` - Get self reference node
- `find_blueprint_nodes` - Find existing nodes in graph

### UMG/UI Operations
- `create_umg_widget_blueprint` - Create UI widget Blueprint
- `add_text_block_to_widget` - Add text elements
- `add_button_to_widget` - Add button elements
- `bind_widget_event` - Bind events to widget components
- `add_widget_to_viewport` - Display widget on screen
- `set_text_block_binding` - Set data bindings for text

### Asset Management
- `list_assets` - List assets in directory
- `get_asset_metadata` - Get asset information
- `search_assets` - Search for assets
- `load_asset` - Load asset into memory
- `save_asset` - Save asset to disk
- `duplicate_asset` - Copy existing asset
- `delete_asset` - Remove asset from project
- `rename_asset` - Rename existing asset
- `move_asset` - Move asset to new location
- `import_asset` - Import external files
- `export_asset` - Export assets to files
- `get_asset_references` - Find asset dependencies
- `get_asset_dependencies` - Find what asset depends on

### Level/World Management
- `create_level` - Create new level
- `save_level` - Save current level
- `load_level` - Load existing level
- `get_current_level_info` - Get level information
- `set_level_visibility` - Control level visibility
- `create_streaming_level` - Add streaming level
- `load_streaming_level` - Load streaming level
- `unload_streaming_level` - Unload streaming level

### Landscape Operations
- `create_landscape` - Create landscape in level
- `modify_landscape` - Modify landscape heightmap
- `paint_landscape_layer` - Paint landscape materials
- `get_landscape_info` - Get landscape information

### Project Operations
- `create_input_mapping` - Create input action mappings

### Utility
- `take_screenshot` - Capture viewport screenshot

## MCP Tool Usage Examples

### Spawning an Actor
```python
# Using MCP tool directly (correct way)
spawn_actor(
    name="MyCube",
    type="StaticMeshActor",
    location=[0, 0, 100],
    rotation=[0, 0, 0],
    static_mesh="/Engine/BasicShapes/Cube.Cube"
)
```

### Creating and Configuring Blueprint
```python
# Create Blueprint
create_blueprint(
    name="MyCharacterBP",
    parent_class="Character"
)

# Add component
add_component_to_blueprint(
    blueprint_name="MyCharacterBP",
    component_type="StaticMeshComponent",
    component_name="MeshComp",
    location=[0, 0, 0]
)

# Set mesh
set_static_mesh_properties(
    blueprint_name="MyCharacterBP",
    component_name="MeshComp",
    static_mesh="/Engine/BasicShapes/Sphere.Sphere"
)

# Compile
compile_blueprint(blueprint_name="MyCharacterBP")
```

### Taking Screenshots for Validation
```python
take_screenshot(
    filename="progress_check",
    show_ui=False,
    resolution=[1920, 1080]
)
```

## Connection Verification

### Before Starting Work
1. Check if Unreal is running (use WSL commands)
2. Verify MCP connection with `/mcp status`
3. Test with simple command like `get_actors_in_level()`

### Connection Test Sequence
```bash
# 1. Check Unreal running (in bash)
powershell.exe -NoProfile -Command "if (Get-Process -Name UnrealEditor -ErrorAction SilentlyContinue) { 'Running' } else { 'Not running' }"

# 2. Check port (in bash)
netstat -an | grep :55557

# 3. Test MCP (use tool)
get_current_level_info()
```

## Error Handling

### Common Issues

#### "MCP not connected"
1. Check if Unreal is running
2. Verify it was started with `-UnrealMCPBind=0.0.0.0`
3. Use `/mcp restart` and select UnrealMCP

#### "Command failed"
1. Check command parameters are correct
2. Verify actor/asset names exist
3. Check Unreal logs for details

#### "Connection timeout"
1. Ensure Windows Firewall allows port 55557
2. Check Windows IP is correct (not 192.168.1.1)
3. Verify Unreal plugin is loaded

## Best Practices

### Tool Usage
1. **Batch Operations**: Group related operations together
2. **Validate Names**: Check if actors/assets exist before operating
3. **Compile Blueprints**: Always compile after modifications
4. **Take Screenshots**: Validate visual changes with screenshots

### Error Recovery
1. **Log Errors**: Check `${PROJECT_ROOT}/Python/unreal_mcp.log`
2. **Retry Logic**: Some operations may need retry after Unreal loads
3. **Graceful Degradation**: Have fallback plans for operations

### Performance
1. **Avoid Polling**: Don't repeatedly check status unnecessarily
2. **Batch Commands**: Send multiple related commands together
3. **Cache Results**: Store query results to avoid repeated lookups

## Passing MCP Guidelines to Sub-Agents

When spawning sub-agents, always include:
```
CRITICAL MCP RULES:
1. Use MCP tools directly - NEVER write Python scripts
2. Check /mcp status before starting
3. If UnrealMCP not connected: /mcp restart and select it
4. All Unreal operations must use MCP tools
5. Validate work with take_screenshot tool
```

## Material and Mesh Notes

### Common Static Meshes
- `/Engine/BasicShapes/Cube.Cube`
- `/Engine/BasicShapes/Sphere.Sphere`
- `/Engine/BasicShapes/Cylinder.Cylinder`
- `/Engine/BasicShapes/Cone.Cone`
- `/Engine/BasicShapes/Plane.Plane`

### Common Materials
- `/Engine/BasicShapes/BasicShapeMaterial`
- `/Engine/MapTemplates/Materials/MI_ProcGrid`
- `/Engine/EngineMaterials/DefaultMaterial`

### Actor Visibility
- Use visibility properties, not scale [0,0,0]
- Set via `set_actor_property(name="ActorName", property_name="bHidden", property_value="false")`