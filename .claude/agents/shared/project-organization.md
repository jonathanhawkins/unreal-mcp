# Unreal Engine Project Organization Standards

This document defines the folder structure and organization standards for Unreal Engine projects, following the [Allar UE5 Style Guide](https://github.com/Allar/ue5-style-guide).

## Core Principles

1. **One Source of Truth**: All project-specific content goes under a single project folder
2. **No Orphans**: Every asset must have a clear, logical location
3. **Scalability**: Structure should support project growth without reorganization
4. **Discoverability**: Anyone should be able to find assets intuitively
5. **Consistency**: Same structure patterns across all projects

## Required Folder Structure

```
Content/
├── [ProjectName]/                 # REQUIRED: All project content here
│   ├── Art/                      # Visual assets
│   │   ├── Materials/            # Materials and instances
│   │   │   ├── Master/          # Master materials (MM_)
│   │   │   ├── Functions/       # Material functions (MF_)
│   │   │   ├── Instances/       # Material instances (MI_)
│   │   │   └── Parameters/      # Parameter collections (MPC_)
│   │   ├── Meshes/              # All mesh assets
│   │   │   ├── Architecture/   # Building parts
│   │   │   ├── Characters/     # Character models
│   │   │   ├── Props/          # Interactive objects
│   │   │   └── Environment/    # Natural elements
│   │   ├── Textures/            # Texture files
│   │   │   ├── Architecture/
│   │   │   ├── Characters/
│   │   │   ├── Props/
│   │   │   ├── Environment/
│   │   │   └── UI/
│   │   └── Animations/          # Animation assets
│   │       ├── Characters/
│   │       │   ├── [CharacterName]/
│   │       │   │   ├── Sequences/    # AS_
│   │       │   │   ├── Montages/     # AM_
│   │       │   │   ├── BlendSpaces/  # BS_
│   │       │   │   └── AnimBP/       # ABP_
│   │       └── Objects/
│   ├── Audio/                   # Sound assets
│   │   ├── Music/              # Background music
│   │   │   ├── Combat/
│   │   │   ├── Exploration/
│   │   │   └── Menu/
│   │   ├── SFX/                # Sound effects
│   │   │   ├── Ambience/
│   │   │   ├── Character/
│   │   │   ├── Footsteps/
│   │   │   ├── Impacts/
│   │   │   ├── UI/
│   │   │   └── Weapons/
│   │   ├── Voice/              # Dialog and voice
│   │   └── Classes/            # Sound classes/mixes
│   ├── Blueprints/             # Blueprint classes
│   │   ├── Core/              # Framework classes
│   │   │   ├── GameModes/    # BP_GM_
│   │   │   ├── GameStates/   # BP_GS_
│   │   │   ├── Controllers/  # BP_PC_, BP_AIC_
│   │   │   └── GameInstance/ # BP_GI_
│   │   ├── Characters/        # Character blueprints
│   │   │   ├── Player/       # BP_PlayerCharacter
│   │   │   ├── NPC/          # BP_NPC_
│   │   │   └── Enemies/      # BP_Enemy_
│   │   ├── Components/        # Actor components
│   │   ├── Interfaces/        # Blueprint interfaces (BPI_)
│   │   ├── Libraries/         # Function libraries (BPFL_)
│   │   ├── Items/            # Interactable items
│   │   │   ├── Weapons/
│   │   │   ├── Pickups/
│   │   │   └── Equipment/
│   │   ├── Systems/          # Game systems
│   │   │   ├── Inventory/
│   │   │   ├── Dialogue/
│   │   │   ├── Quest/
│   │   │   └── Save/
│   │   └── Utilities/        # Helper blueprints
│   ├── Data/                 # Data-driven assets
│   │   ├── DataAssets/      # DA_
│   │   ├── DataTables/      # DT_
│   │   ├── Curves/          # C_
│   │   └── Configs/         # Configuration files
│   ├── Effects/             # Visual effects
│   │   ├── Niagara/        # Niagara systems
│   │   │   ├── Systems/    # NS_
│   │   │   ├── Emitters/   # NE_
│   │   │   └── Functions/  # NF_
│   │   ├── Materials/      # Effect materials
│   │   └── Textures/       # Effect textures
│   ├── Maps/               # Level files
│   │   ├── Episodes/       # Main game levels
│   │   │   ├── Episode01/
│   │   │   │   ├── L_E01_Persistent
│   │   │   │   ├── L_E01_Gameplay
│   │   │   │   ├── L_E01_Lighting
│   │   │   │   ├── L_E01_Audio
│   │   │   │   └── L_E01_Cinematics
│   │   ├── Gyms/          # Test/prototype levels
│   │   └── DevMaps/       # Development test maps
│   ├── UI/                # User interface
│   │   ├── HUD/          # In-game UI
│   │   ├── Menus/        # Menu screens
│   │   │   ├── MainMenu/
│   │   │   ├── PauseMenu/
│   │   │   └── Settings/
│   │   ├── Widgets/      # Reusable widgets
│   │   ├── Icons/        # UI icons
│   │   └── Fonts/        # Typography
│   └── Cinematics/       # Cutscenes and sequences
│       ├── Sequences/    # LS_
│       ├── Cameras/      # Camera assets
│       └── PostProcess/  # PP volumes/materials
├── Developers/           # Personal folders (never ship)
│   └── [DeveloperName]/ # Individual test content
├── Engine/              # Engine content (READ-ONLY)
└── Plugins/            # Plugin content (organized by plugin)
```

## Folder Rules and Guidelines

### Mandatory Rules
1. **Project Folder**: ALL project content MUST be under `/Content/[ProjectName]/`
2. **No Root Assets**: NEVER place assets directly in `/Content/`
3. **Developer Folders**: Test content MUST go in `/Content/Developers/[YourName]/`
4. **Asset Counts**: If >15 similar assets, create subfolders
5. **Folder Depth**: Maximum 5 levels deep (performance and usability)
6. **Naming**: No spaces, special characters (except underscore)

### Organization by Asset Type

#### Materials Organization
```
Materials/
├── Master/           # Master materials only
│   ├── MM_Character
│   ├── MM_Environment
│   └── MM_Weapon
├── Instances/       # Material instances
│   ├── Characters/
│   ├── Environment/
│   └── Weapons/
└── Functions/       # Shared material functions
    ├── MF_Fresnel
    └── MF_WorldAlignedTexture
```

#### Blueprint Organization
```
Blueprints/
├── Core/           # ONLY framework classes
├── Characters/     # Grouped by character type
├── Components/     # Reusable components
├── Systems/        # Major game systems
└── Utilities/      # Helper/debug blueprints
```

#### Level Organization
```
Maps/
├── Episodes/       # Shipped levels
│   └── Episode01/
│       ├── L_E01_Persistent    # Always loaded
│       ├── L_E01_Gameplay      # Gameplay elements
│       ├── L_E01_Lighting      # Lights and sky
│       ├── L_E01_Audio         # Sound actors
│       ├── L_E01_Effects       # VFX
│       └── L_E01_Cinematics    # Cutscenes
├── Gyms/          # Feature test levels
│   ├── GYM_Combat
│   ├── GYM_Movement
│   └── GYM_Lighting
└── DevMaps/       # Quick test maps
    └── DEV_MaterialTest
```

## Asset Migration Rules

### When Moving Assets
1. Fix all references BEFORE moving
2. Use "Move" command, not copy/paste
3. Update any hardcoded paths
4. Verify no broken references after move
5. Submit redirectors with changelist

### When Renaming Assets
1. Use "Rename" command in Content Browser
2. Never rename by editing .uasset filename
3. Fix all Blueprint compile errors
4. Update any string references
5. Clean up redirectors before submit

## Special Folders

### Developers Folder
- **Purpose**: Personal testing and experiments
- **Rules**:
  - Never reference from production assets
  - Not included in shipping builds
  - Each developer has own subfolder
  - Can be messy/unorganized
  - Delete content regularly

### External Content
```
Content/
├── [ProjectName]/     # Your content
├── MarketplaceContent/ # Marketplace assets
├── ImportedContent/    # External sources
└── ThirdParty/        # Licensed content
```

## Quality Validation

### Folder Structure Checklist
- [ ] All content under project folder
- [ ] No assets in Content root
- [ ] Clear folder purposes
- [ ] Consistent subfolder patterns
- [ ] No "Temp" or "Test" in production
- [ ] Materials organized by type
- [ ] Blueprints grouped logically
- [ ] Maps follow naming convention

### MCP Validation Script
```python
# Check folder structure
assets = list_assets(path="/Game", recursive=True)

# Validate no root assets
root_assets = list_assets(path="/Game", recursive=False)
if root_assets:
    print("ERROR: Assets found in root Content folder")

# Check project folder exists
project_assets = list_assets(path="/Game/[ProjectName]", recursive=False)
if not project_assets:
    print("ERROR: Project folder not found")

# Verify map organization
maps = list_assets(path="/Game/[ProjectName]/Maps", type_filter="World")
for map in maps:
    # Ensure proper prefixing
    if not map.startswith("L_"):
        print(f"WARNING: Map {map} missing L_ prefix")
```

## Migration from Poor Structure

### Step 1: Audit Current Structure
```python
# Generate asset report
all_assets = list_assets(path="/Game", recursive=True)
# Export to CSV for analysis
```

### Step 2: Create New Structure
1. Create project folder
2. Create all subfolders
3. Don't move assets yet

### Step 3: Migrate by Type
1. Materials first (fewer dependencies)
2. Textures second
3. Meshes third
4. Blueprints last (most dependencies)

### Step 4: Fix References
```python
# Check for broken references
get_asset_references(asset_path="/Game/[AssetPath]")
get_asset_dependencies(asset_path="/Game/[AssetPath]")
```

### Step 5: Clean Redirectors
1. Fix all references
2. Delete redirectors
3. Submit clean changelist

## Common Mistakes

### DON'T
- ❌ Mix asset types in same folder
- ❌ Create folders named "Misc" or "Stuff"
- ❌ Use version numbers in folder names
- ❌ Create personal folders in production
- ❌ Duplicate folder structures
- ❌ Use dates in folder names
- ❌ Create empty placeholder folders

### DO
- ✅ Group by function, not asset type
- ✅ Use clear, descriptive names
- ✅ Keep related assets together
- ✅ Plan structure before starting
- ✅ Document special folders
- ✅ Regular structure audits
- ✅ Train team on standards

## Enforcement

### Automated Checks
- Pre-commit hooks validate structure
- CI/CD pipeline checks organization
- Weekly structure reports
- Automated cleanup suggestions

### Manual Reviews
- Code review includes structure check
- Monthly folder audit
- Quarterly cleanup sprints
- New team member training

## References
- [Allar's UE5 Style Guide - Project Structure](https://github.com/Allar/ue5-style-guide#2-content-directory-structure)
- [Epic's Content Guidelines](https://docs.unrealengine.com/5.0/en-US/content-guidelines-for-unreal-engine/)
- [UE5 Best Practices](https://docs.unrealengine.com/5.0/en-US/content-best-practices-for-unreal-engine/)