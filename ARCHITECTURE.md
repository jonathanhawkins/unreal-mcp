# Unreal MCP Architecture

## Modular Organization Strategy

To prevent files from becoming too large and maintain scalability, we're organizing the codebase into focused modules.

## C++ Plugin Structure

```
MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/
├── Public/
│   ├── Core/                    # Core infrastructure
│   │   ├── UnrealMCPBridge.h
│   │   └── MCPServerRunnable.h
│   ├── Commands/                # Command handlers (modular)
│   │   ├── Base/
│   │   │   └── UnrealMCPCommandBase.h
│   │   ├── Editor/
│   │   │   └── UnrealMCPEditorCommands.h
│   │   ├── Blueprint/
│   │   │   ├── UnrealMCPBlueprintCommands.h
│   │   │   └── UnrealMCPBlueprintNodeCommands.h
│   │   ├── Assets/              # NEW - Phase 1
│   │   │   └── UnrealMCPAssetCommands.h
│   │   ├── World/               # NEW - Phase 1
│   │   │   └── UnrealMCPWorldCommands.h
│   │   ├── Materials/           # NEW - Phase 2
│   │   │   └── UnrealMCPMaterialCommands.h
│   │   ├── Lighting/            # NEW - Phase 2
│   │   │   └── UnrealMCPLightingCommands.h
│   │   ├── PostProcess/         # NEW - Phase 2
│   │   │   └── UnrealMCPPostProcessCommands.h
│   │   ├── Niagara/            # NEW - Phase 3
│   │   │   └── UnrealMCPNiagaraCommands.h
│   │   ├── Animation/          # NEW - Phase 3
│   │   │   └── UnrealMCPAnimationCommands.h
│   │   ├── Audio/              # NEW - Phase 3
│   │   │   └── UnrealMCPAudioCommands.h
│   │   ├── AI/                 # NEW - Phase 4
│   │   │   └── UnrealMCPAICommands.h
│   │   └── Physics/            # NEW - Phase 4
│   │       └── UnrealMCPPhysicsCommands.h
│   └── Utils/
│       └── UnrealMCPHelpers.h
└── Private/
    └── [Mirror structure of Public]
```

## Python Server Structure

```
Python/
├── unreal_mcp_server.py         # Main server entry
├── core/                        # Core infrastructure
│   ├── connection.py           # UnrealConnection class
│   ├── protocol.py             # JSON protocol handling
│   └── utils.py                # Shared utilities
├── tools/                       # MCP tool implementations
│   ├── base.py                 # Base tool class
│   ├── editor_tools.py         # Editor operations
│   ├── blueprint_tools.py      # Blueprint operations
│   ├── node_tools.py           # Node graph operations
│   ├── umg_tools.py           # UI/UMG operations
│   ├── project_tools.py       # Project operations
│   ├── assets/                 # NEW - Phase 1
│   │   ├── asset_tools.py     # Asset management
│   │   └── content_browser.py # Content browser ops
│   ├── world/                  # NEW - Phase 1
│   │   ├── level_tools.py     # Level management
│   │   └── landscape_tools.py # Landscape editing
│   ├── materials/              # NEW - Phase 2
│   │   ├── material_tools.py  # Material creation
│   │   └── texture_tools.py   # Texture operations
│   ├── lighting/               # NEW - Phase 2
│   │   └── lighting_tools.py  # Light management
│   ├── postprocess/            # NEW - Phase 2
│   │   └── postprocess_tools.py
│   ├── niagara/               # NEW - Phase 3
│   │   └── particle_tools.py
│   ├── animation/             # NEW - Phase 3
│   │   ├── sequencer_tools.py
│   │   └── anim_tools.py
│   ├── audio/                 # NEW - Phase 3
│   │   └── metasound_tools.py
│   ├── ai/                    # NEW - Phase 4
│   │   └── ai_tools.py
│   └── physics/               # NEW - Phase 4
│       └── physics_tools.py
├── tests/                      # Test scripts
│   └── [organized by module]
└── scripts/                    # Example scripts
    └── [organized by feature]
```

## Design Principles

1. **Single Responsibility**: Each module handles one aspect of Unreal Engine
2. **Loose Coupling**: Modules communicate through well-defined interfaces
3. **High Cohesion**: Related functionality stays together
4. **Testability**: Each module can be tested independently
5. **Extensibility**: New features can be added without modifying existing code

## Module Size Guidelines

- Max lines per file: 500-800 lines
- When a file exceeds 500 lines, consider splitting into sub-modules
- Each command handler should be self-contained
- Shared utilities go in Utils/Helpers modules

## Testing Strategy

Each new module will have:
1. Unit tests in `tests/unit/[module]/`
2. Integration tests in `tests/integration/[module]/`
3. Example scripts in `scripts/[module]/`

## Implementation Phases

### Phase 1: Core Enhancements (Current)
- Asset Management Tools
- Advanced World/Level Tools
- Direct Engine Access

### Phase 2: Material & Visual Systems
- Material Editor
- Lighting System
- Post Processing

### Phase 3: Advanced Systems
- Niagara Particle Systems
- Animation & Sequencer
- Audio - Metasound

### Phase 4: AI & Gameplay
- AI/Navigation
- Physics Simulation
- Gameplay Framework

### Phase 5: Code Intelligence
- Code Analysis
- Documentation Integration

### Phase 6: Advanced Automation
- Procedural Generation
- Optimization Tools
- Build & Deploy