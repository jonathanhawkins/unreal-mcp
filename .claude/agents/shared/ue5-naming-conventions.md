# Unreal Engine 5 Naming Conventions

This document defines the naming standards for all Unreal Engine assets, following the [Allar UE5 Style Guide](https://github.com/Allar/ue5-style-guide).

## Core Principle
All assets should follow the pattern: `Prefix_BaseAssetName_Variant_Suffix`

## Asset Type Prefixes

### Blueprints
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Blueprint | BP_ | BP_PlayerCharacter |
| Blueprint Interface | BPI_ | BPI_Interactable |
| Blueprint Function Library | BPFL_ | BPFL_MathHelpers |
| Blueprint Macro Library | BPML_ | BPML_FlowMacros |
| Enumeration | E_ | E_WeaponType |
| Structure | F_ or S_ | F_ItemData |
| Widget Blueprint | WBP_ | WBP_MainMenu |
| Anim Blueprint | ABP_ | ABP_Character |

### Meshes and Geometry
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Static Mesh | SM_ | SM_Rock_01 |
| Skeletal Mesh | SK_ | SK_Character |
| Geometry Collection | GC_ | GC_Building |
| Nanite Mesh | NM_ | NM_HighDetail |

### Materials and Textures
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Material | M_ | M_Wood_Oak |
| Material Instance | MI_ | MI_Wood_Oak_Worn |
| Material Function | MF_ | MF_Noise |
| Material Parameter Collection | MPC_ | MPC_GlobalParams |
| Texture | T_ | T_Wood_D |
| Render Target | RT_ | RT_MinimapCapture |
| Texture Cube | TC_ | TC_SkyHDRI |
| Media Texture | MT_ | MT_VideoScreen |

### Texture Suffixes
| Texture Type | Suffix | Example |
|-------------|---------|---------|
| Diffuse/Albedo | _D | T_Wood_D |
| Normal | _N | T_Wood_N |
| Roughness | _R | T_Wood_R |
| Metallic | _M | T_Wood_M |
| Emissive | _E | T_Wood_E |
| Ambient Occlusion | _AO | T_Wood_AO |
| Opacity | _O | T_Wood_O |
| Mask | _Mask | T_Wood_Mask |
| Height/Displacement | _H | T_Wood_H |

### Animation
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Animation Sequence | AS_ | AS_Character_Run |
| Animation Montage | AM_ | AM_Character_Attack |
| Aim Offset | AO_ | AO_Character_Aim |
| Blend Space | BS_ | BS_Character_Locomotion |
| Level Sequence | LS_ | LS_Cutscene_Intro |
| Morph Target | MT_ | MT_Face_Smile |
| Paper Flipbook | PFB_ | PFB_Explosion |
| Rig | Rig_ | Rig_Character |
| Control Rig | CR_ | CR_Character |

### Audio
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Sound Wave | S_ | S_Explosion |
| Sound Cue | SC_ | SC_Footstep |
| Sound Attenuation | SA_ | SA_Outdoor |
| Sound Class | SCL_ | SCL_Music |
| Sound Mix | SMix_ | SMix_Combat |
| Dialogue Voice | DV_ | DV_NPC_Greeting |
| Dialogue Wave | DW_ | DW_Conversation |

### Physics
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Physical Material | PM_ | PM_Wood |
| Physics Asset | PHYS_ | PHYS_Character |
| Destructible Mesh | DM_ | DM_Wall |

### AI
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Behavior Tree | BT_ | BT_Enemy |
| Blackboard | BB_ | BB_Enemy |
| Decorator | BTDecorator_ | BTDecorator_IsInRange |
| Service | BTService_ | BTService_UpdateTarget |
| Task | BTTask_ | BTTask_Attack |
| Environment Query | EQS_ | EQS_FindCover |
| AI Controller | AIC_ | AIC_Enemy |

### Particles and Effects
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Particle System | PS_ | PS_Fire |
| Niagara Emitter | NE_ | NE_Sparks |
| Niagara System | NS_ | NS_Explosion |
| Niagara Function | NF_ | NF_SpawnBurst |
| Niagara Module | NM_ | NM_ColorOverLife |
| Niagara Dynamic Input | NDI_ | NDI_GridData |

### UI
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Widget Blueprint | WBP_ | WBP_HUD |
| Font | Font_ | Font_RobotoRegular |
| Slate Widget Style | SWS_ | SWS_Button |
| Slate Brush | SB_ | SB_ButtonNormal |

### Miscellaneous
| Asset Type | Prefix | Example |
|------------|--------|---------|
| Level/Map | L_ | L_MainMenu (but often no prefix) |
| Level Instance | LI_ | LI_Building |
| Data Asset | DA_ | DA_ItemDatabase |
| Data Table | DT_ | DT_WeaponStats |
| Curve | C_ | C_DamageFalloff |
| Curve Table | CT_ | CT_NPCStats |
| Foliage Type | FT_ | FT_Pine |
| Landscape Layer | LL_ | LL_Grass |
| World | W_ | W_Persistent |

## Variable Naming Conventions

### Blueprint Variables
| Type | Prefix | Example |
|------|--------|---------|
| Boolean | b | bIsAlive |
| Integer | i | iHealth |
| Float | f | fSpeed |
| String | s | sPlayerName |
| Name | n | nSocketName |
| Text | t | tDisplayText |
| Vector | v | vLocation |
| Rotator | r | rRotation |
| Transform | tr | trWorldTransform |
| Object Reference | o | oPlayerController |
| Class | c | cEnemyClass |
| Array | a | aInventoryItems |
| Map | m | mItemPrices |
| Set | set | setVisitedRooms |

### Function Naming
- Use **PascalCase** for function names
- Functions should be **verbs** that describe actions
- Event handlers should start with "On": `OnHealthChanged`
- Getters don't need "Get" prefix: `Health()` not `GetHealth()`
- Setters should use "Set" prefix: `SetHealth()`
- Boolean checks should ask questions: `IsAlive()`, `CanFire()`, `HasWeapon()`

### C++ Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase with prefix | AMyActor, UMyObject |
| Structs | PascalCase with F prefix | FMyStruct |
| Enums | PascalCase with E prefix | EWeaponType |
| Interfaces | PascalCase with I prefix | IInteractable |
| Functions | PascalCase | CalculateDamage() |
| Variables | PascalCase | Health, PlayerName |
| Private Members | PascalCase | MyPrivateVariable |
| Parameters | PascalCase | InDamage, OutResult |
| Constants | UPPER_CASE | MAX_HEALTH |

## Folder Structure

### Top-Level Organization
```
Content/
├── ProjectName/          # All project-specific content
│   ├── Art/             # Art assets
│   │   ├── Materials/
│   │   ├── Textures/
│   │   ├── Meshes/
│   │   └── Animations/
│   ├── Audio/           # Sound and music
│   │   ├── Music/
│   │   ├── SFX/
│   │   └── Voice/
│   ├── Blueprints/      # Core blueprints
│   │   ├── Core/        # GameMode, GameState, etc.
│   │   ├── Characters/
│   │   ├── Items/
│   │   └── Systems/
│   ├── Data/            # Data assets and tables
│   ├── Effects/         # VFX and particles
│   ├── Maps/            # All levels
│   │   ├── MainGame/
│   │   └── TestMaps/
│   ├── UI/              # User interface
│   └── Developers/      # Personal test content
├── Engine/              # Engine content (read-only)
└── Plugins/            # Plugin content
```

### Asset-Specific Rules
1. **Never** use spaces in file names (use PascalCase or underscores)
2. **Always** include variant numbers with padding: `_01`, `_02` not `_1`, `_2`
3. **Group** related assets in subfolders when count exceeds 10
4. **Avoid** generic folder names like "Assets", "Misc", "Stuff"
5. **Use** clear descriptive names: `T_Wood_Oak_D` not `T_W_O_D`

## Blueprint Organization

### Graph Structure
1. **Event Graph**: Main gameplay logic
2. **Functions**: Reusable logic (50 nodes max per function)
3. **Macros**: Compile-time expanded code
4. **Construction Script**: Object initialization

### Node Organization
- Group related nodes with comments
- Align nodes to grid
- Minimize wire crossing
- Flow left-to-right or top-to-bottom
- Use reroute nodes for clarity
- Color-code comment boxes by system

### Variable Organization
- Group variables by category
- Use clear descriptions
- Mark replication settings properly
- Set appropriate access specifiers
- Initialize default values

## Material Conventions

### Material Instances
- Always create from master materials
- Group parameters logically
- Use clear parameter names
- Document parameter ranges

### Master Materials
- Prefix with `MM_`: `MM_Environment`
- Create reusable, parameterized materials
- Optimize for target platform
- Include quality scalability

## Quality Checklist

### Before Commit
- [ ] Assets follow naming conventions
- [ ] Files in correct folders
- [ ] No spaces in file names
- [ ] Blueprints compiled without errors
- [ ] Materials have proper LODs
- [ ] Textures have correct compression
- [ ] Meshes have collision and LODs
- [ ] No missing asset references

### MCP Validation Commands
```python
# Verify asset naming
assets = list_assets(path="/Game/ProjectName", recursive=True)
# Check for naming convention violations

# Compile all blueprints
compile_blueprint(blueprint_name="BP_PlayerCharacter")

# Check for missing references
get_asset_dependencies(asset_path="/Game/Maps/MainLevel")
```

## Common Mistakes to Avoid

1. **DON'T** use generic names: ~~`Material1`~~, ~~`NewBlueprint`~~
2. **DON'T** mix naming conventions in same project
3. **DON'T** put assets in root Content folder
4. **DON'T** use special characters except underscore
5. **DON'T** create deep folder hierarchies (max 4 levels)
6. **DON'T** duplicate assets without clear variants
7. **DON'T** leave test/temp assets in production folders

## References
- [Allar's UE5 Style Guide](https://github.com/Allar/ue5-style-guide)
- [Epic's Coding Standards](https://docs.unrealengine.com/5.0/en-US/epic-cplusplus-coding-standard-for-unreal-engine/)
- [UE5 Best Practices](https://docs.unrealengine.com/5.0/en-US/recommended-asset-naming-conventions-in-unreal-engine-projects/)