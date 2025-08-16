# Blueprint Development Standards

This document defines the standards for Blueprint development in Unreal Engine 5, following the [Allar UE5 Style Guide](https://github.com/Allar/ue5-style-guide) and best practices.

## Core Principles

1. **Readability**: Blueprints should be self-documenting
2. **Maintainability**: Easy to modify and extend
3. **Performance**: Optimized for runtime efficiency
4. **Reusability**: Components and functions should be modular
5. **Consistency**: Follow same patterns throughout project

## Blueprint Naming Standards

### Class Naming
| Blueprint Type | Prefix | Example |
|---------------|--------|---------|
| Actor | BP_ | BP_Door |
| Character | BP_ | BP_PlayerCharacter |
| Game Mode | BP_GM_ | BP_GM_Deathmatch |
| Game State | BP_GS_ | BP_GS_Match |
| Player Controller | BP_PC_ | BP_PC_InGame |
| AI Controller | BP_AIC_ | BP_AIC_Enemy |
| Player State | BP_PS_ | BP_PS_Player |
| HUD | BP_HUD_ | BP_HUD_InGame |
| Widget | WBP_ | WBP_MainMenu |
| Animation Blueprint | ABP_ | ABP_Character |
| Interface | BPI_ | BPI_Interactable |
| Function Library | BPFL_ | BPFL_GameHelpers |
| Macro Library | BPML_ | BPML_NodeHelpers |

## Variable Standards

### Variable Naming Convention
```
[Prefix][DescriptiveName]
```

### Variable Prefixes
| Type | Prefix | Example |
|------|--------|---------|
| Boolean | b | bIsAlive, bCanFire |
| Integer | i | iAmmoCount, iScore |
| Float | f | fHealth, fSpeed |
| Name | n | nBoneName |
| String | s | sPlayerName |
| Text | t | tDescription |
| Vector | v | vLocation |
| Rotator | r | rAimRotation |
| Transform | tr | trSpawnTransform |
| Object | o | oGameMode |
| Actor | a | aTargetActor |
| Component | c | cMeshComponent |
| Class | class | classEnemyType |
| Array | a | aInventoryItems |
| Map | m | mItemPrices |
| Set | set | setVisitedRooms |
| Enum | e | eWeaponType |
| Struct | st | stPlayerData |

### Variable Organization
```
Blueprint Variables Panel:
├── Config (Instance Editable)
│   ├── Gameplay
│   ├── Visual
│   └── Audio
├── State (Private)
│   ├── Health
│   ├── Movement
│   └── Combat
├── References (Private)
│   ├── Components
│   ├── Actors
│   └── Widgets
└── Cache (Private/Transient)
    ├── Calculations
    └── Temporaries
```

### Variable Properties
- **Always** add descriptions
- **Set** appropriate categories
- **Mark** replication settings
- **Configure** access specifiers
- **Initialize** default values
- **Use** appropriate data types

## Function Standards

### Function Naming
- **Use PascalCase**: `CalculateDamage`, `SpawnProjectile`
- **Start with verb**: `Get`, `Set`, `Calculate`, `Spawn`, `Update`
- **Be descriptive**: `GetPlayerHealthPercentage` not `GetHP`
- **Boolean functions ask questions**: `IsAlive`, `CanFire`, `HasAmmo`

### Function Categories
```
Functions:
├── Core
│   ├── Initialize
│   ├── BeginPlay
│   └── Tick
├── Gameplay
│   ├── Combat
│   ├── Movement
│   └── Interaction
├── Getters
│   ├── GetHealth
│   └── GetSpeed
├── Setters
│   ├── SetHealth
│   └── SetSpeed
├── Events
│   ├── OnDeath
│   ├── OnDamaged
│   └── OnInteract
└── Utilities
    ├── Debug
    └── Helpers
```

### Function Rules
1. **Maximum 50 nodes** per function
2. **Single responsibility** principle
3. **Pure functions** when possible
4. **Local variables** for clarity
5. **Return values** documented
6. **Input validation** at start

### Function Documentation
```
Function: CalculateDamage
Description: Calculates final damage after applying armor and resistances
Inputs:
  - BaseDamage (Float): Raw damage before mitigation
  - DamageType (Enum): Type of damage being applied
Outputs:
  - FinalDamage (Float): Damage after all calculations
```

## Graph Organization

### Node Layout Rules
1. **Flow Direction**: Left-to-right or top-to-bottom
2. **Node Alignment**: Snap to grid
3. **Wire Management**: Minimize crossings
4. **Spacing**: Consistent gaps between nodes
5. **Grouping**: Related nodes together

### Comment Standards
```
Comment Box Colors:
- 🔴 Red: Critical/Temporary code
- 🟠 Orange: Needs optimization
- 🟡 Yellow: Gameplay logic
- 🟢 Green: Initialization/Setup
- 🔵 Blue: Input handling
- 🟣 Purple: Audio/Visual
- ⚫ Gray: Debug/Development
- ⚪ White: General comments
```

### Comment Format
```
[SYSTEM NAME]
Brief description of what this section does
TODO: Any pending tasks
NOTE: Important information
WARNING: Potential issues
```

### Execution Flow
```
Event BeginPlay
    ├── Initialize Variables
    ├── Setup Components
    ├── Bind Events
    └── Start Gameplay Systems
```

## Component Architecture

### Component Usage
- **ActorComponent**: Non-visual logic
- **SceneComponent**: Transform without visuals
- **StaticMeshComponent**: Static geometry
- **SkeletalMeshComponent**: Animated meshes
- **Custom Components**: Modular functionality

### Component Naming
```
Root
├── CollisionCapsule
├── CharacterMesh
├── WeaponSocket
│   └── WeaponMesh
├── CameraArm
│   └── FollowCamera
└── AudioComponent
```

## Event Handling

### Event Naming Convention
- **Input Events**: `Input_[Action]` → `Input_Jump`
- **Collision Events**: `On[Event]` → `OnBeginOverlap`
- **Damage Events**: `On[Event]` → `OnTakeDamage`
- **Custom Events**: `[Verb][Subject]` → `UpdateHealthBar`

### Event Dispatchers
```
Naming: On[Subject][Action]
Examples:
- OnHealthChanged
- OnWeaponFired
- OnEnemySpawned
```

### Event Best Practices
1. **Unbind** events when not needed
2. **Validate** event parameters
3. **Avoid** circular event calls
4. **Document** event flow
5. **Use** event dispatchers for decoupling

## Performance Guidelines

### Tick Optimization
```cpp
// BAD: Heavy logic in Tick
Event Tick
    └── Complex Calculations

// GOOD: Use timers or conditions
Event Tick
    └── If (Should Update)
        └── Simple Update

// BETTER: Use timer
Set Timer by Event (0.1 seconds)
    └── Update Logic
```

### Common Optimizations
1. **Cache** expensive lookups
2. **Use** object pooling
3. **Limit** tick usage
4. **Optimize** collision channels
5. **Profile** Blueprint performance
6. **Avoid** nested loops
7. **Use** C++ for heavy math

### Performance Patterns
```
DO:
✅ Cache component references
✅ Use IsValid checks
✅ Gate expensive operations
✅ Use events over tick
✅ Profile regularly

DON'T:
❌ Get All Actors every frame
❌ Spawn/Destroy frequently
❌ Complex math in Blueprint
❌ Deep inheritance chains
❌ Circular dependencies
```

## Inheritance and Interfaces

### Inheritance Hierarchy
```
BP_Character_Base (Abstract)
    ├── BP_Character_Player
    │   ├── BP_Character_Warrior
    │   └── BP_Character_Mage
    └── BP_Character_NPC
        ├── BP_Character_Merchant
        └── BP_Character_Guard
```

### Interface Usage
```
BPI_Interactable
    - Interact(Actor: Instigator)
    - GetInteractionText() → Text
    - CanInteract(Actor: Instigator) → Bool

Implementation:
BP_Door implements BPI_Interactable
BP_Chest implements BPI_Interactable
BP_NPC implements BPI_Interactable
```

## Replication Standards

### Replicated Variables
```
Variable Properties:
- Replication: Replicated
- RepNotify: OnRep_Health
- Condition: COND_OwnerOnly
```

### Replication Rules
1. **Minimize** replicated variables
2. **Use** RepNotify for UI updates
3. **Validate** on server
4. **Predict** on client
5. **Document** network behavior

## Debugging Standards

### Debug Visualization
```
Debug Draw:
- Print String: Temporary info
- Draw Debug Line: Paths
- Draw Debug Sphere: Positions
- Draw Debug Box: Bounds
```

### Debug Categories
```
Console Variables:
- DebugMovement
- DebugCombat
- DebugAI
- DebugNetwork
```

## Quality Checklist

### Before Commit
- [ ] Blueprint compiles without errors
- [ ] No compiler warnings
- [ ] Functions under 50 nodes
- [ ] Variables have descriptions
- [ ] Comments explain complex logic
- [ ] No deprecated nodes
- [ ] Proper error handling
- [ ] Optimized tick usage

### Code Review Checklist
- [ ] Naming conventions followed
- [ ] Graph is readable
- [ ] Logic is efficient
- [ ] Replication configured
- [ ] Events properly bound/unbound
- [ ] No hardcoded values
- [ ] Uses project systems

## MCP Validation

### Blueprint Compilation
```python
# Compile Blueprint
compile_blueprint(blueprint_name="BP_PlayerCharacter")

# Check for specific nodes
nodes = find_blueprint_nodes(
    blueprint_name="BP_PlayerCharacter",
    node_type="Event"
)

# Verify no tick events in non-essential blueprints
tick_nodes = find_blueprint_nodes(
    blueprint_name="BP_Prop",
    event_type="Tick"
)
if tick_nodes:
    print("WARNING: Tick event in prop blueprint")
```

### Blueprint Analysis
```python
# Add variable
add_blueprint_variable(
    blueprint_name="BP_Character",
    variable_name="bIsAlive",
    variable_type="Boolean",
    is_exposed=True
)

# Create function node
add_blueprint_function_node(
    blueprint_name="BP_Character",
    target="self",
    function_name="TakeDamage",
    params={"DamageAmount": "100.0"}
)

# Connect nodes
connect_blueprint_nodes(
    blueprint_name="BP_Character",
    source_node_id="BeginPlay",
    source_pin="exec",
    target_node_id="InitializeHealth",
    target_pin="exec"
)
```

## Common Mistakes

### DON'T
- ❌ Leave compile errors
- ❌ Use Tick for everything
- ❌ Create spaghetti graphs
- ❌ Ignore warnings
- ❌ Skip documentation
- ❌ Hardcode values
- ❌ Create circular dependencies

### DO
- ✅ Keep graphs clean
- ✅ Use comments liberally
- ✅ Validate inputs
- ✅ Handle errors gracefully
- ✅ Profile performance
- ✅ Test edge cases
- ✅ Document complex logic

## Advanced Patterns

### State Machine Pattern
```
Enum: ECharacterState
- Idle
- Moving
- Attacking
- Dead

Switch on ECharacterState
    ├── Idle → IdleLogic()
    ├── Moving → MovementLogic()
    ├── Attacking → AttackLogic()
    └── Dead → DeathLogic()
```

### Object Pool Pattern
```
Array: PooledProjectiles
- Spawn N projectiles at start
- Deactivate instead of destroy
- Reactivate from pool
- Return to pool when done
```

### Observer Pattern
```
Event Dispatcher: OnHealthChanged
- UI subscribes to update health bar
- AI subscribes to change behavior
- Audio subscribes to play hurt sound
```

## References
- [Allar's UE5 Style Guide - Blueprints](https://github.com/Allar/ue5-style-guide#4-blueprints)
- [UE5 Blueprint Best Practices](https://docs.unrealengine.com/5.0/en-US/blueprint-best-practices-in-unreal-engine/)
- [Blueprint Optimization](https://docs.unrealengine.com/5.0/en-US/blueprint-optimization-in-unreal-engine/)