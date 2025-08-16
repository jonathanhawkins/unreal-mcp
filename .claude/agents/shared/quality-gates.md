# Quality Gates by Development Phase

This document defines quality standards and acceptance criteria for each phase of game development.

## Development Phases Overview

```
PROTOTYPE → DEVELOPMENT → POLISH → SHIP
```

Each phase has specific goals, standards, and exit criteria that must be met before proceeding.

## Phase 1: PROTOTYPE

### Goal
Prove core concepts and validate game ideas quickly.

### Quality Standards
- **Functionality**: Core mechanics work (even if rough)
- **Performance**: 30+ FPS acceptable
- **Visuals**: Placeholder assets and basic shapes OK
- **Code**: Quick and dirty acceptable, focus on iteration
- **Stability**: Crashes acceptable if documented

### Acceptance Criteria
- [ ] Core gameplay loop demonstrated
- [ ] Key mechanics functional
- [ ] Basic controls implemented
- [ ] Concept proven viable
- [ ] Major technical risks identified

### MCP Validation
```python
# Take wide screenshot showing core mechanic
take_screenshot(filename="prototype_core_mechanic", show_ui=True)

# List all prototype actors
get_actors_in_level()
```

### What's Acceptable
- Hardcoded values
- Temporary UI
- Debug visualizations
- Placeholder sounds
- Basic collisions
- Simple materials

### What's NOT Required
- Optimization
- Final art
- Complete features
- Error handling
- Save system
- Menus

## Phase 2: DEVELOPMENT

### Goal
Build robust, scalable systems with proper architecture.

### Quality Standards
- **Functionality**: All features fully implemented
- **Performance**: Stable 60 FPS on target hardware
- **Visuals**: Production-ready pipeline established
- **Code**: Clean, maintainable, documented
- **Stability**: No frequent crashes

### Acceptance Criteria
- [ ] All planned features implemented
- [ ] Systems properly architected
- [ ] Data-driven design where appropriate
- [ ] Multiplayer foundation (if applicable)
- [ ] Basic optimization pass complete
- [ ] Core art pipeline established

### MCP Validation
```python
# Compile all Blueprints
compile_blueprint(blueprint_name="GameModeBP")
compile_blueprint(blueprint_name="PlayerControllerBP")

# Verify level structure
get_current_level_info()

# Check asset organization
list_assets(path="/Game", recursive=True)
```

### Required Standards
- **Blueprints**: Compiled, organized, commented
- **C++**: Following UE coding standards
- **Assets**: Proper naming convention
- **Levels**: Streaming setup if needed
- **UI**: Functional with proper bindings
- **Audio**: System architecture in place

### Architecture Requirements
- Modular component design
- Clear separation of concerns
- Reusable systems
- Proper inheritance hierarchy
- Event-driven communication

## Phase 3: POLISH

### Goal
Refine user experience and optimize performance.

### Quality Standards
- **Functionality**: All features polished and refined
- **Performance**: Consistent 60+ FPS, optimized
- **Visuals**: Final art, effects, and lighting
- **Code**: Optimized, profiled, refined
- **Stability**: Rare crashes only

### Acceptance Criteria
- [ ] Performance profiled and optimized
- [ ] Visual effects and polish applied
- [ ] UI/UX refined and tested
- [ ] Audio mixed and balanced
- [ ] Animations polished
- [ ] Game feel tuned

### MCP Validation
```python
# Take beauty shots
take_screenshot(filename="polish_beauty_1", show_ui=False, resolution=[3840, 2160])

# Verify all materials assigned
search_assets(search_text="Material", type_filter="Material")

# Check Blueprint complexity
find_blueprint_nodes(blueprint_name="PlayerCharacterBP")
```

### Polish Checklist
- **Visual Polish**
  - [ ] Final materials and textures
  - [ ] Lighting passes complete
  - [ ] Post-processing tuned
  - [ ] Particle effects added
  - [ ] LODs implemented

- **Gameplay Polish**
  - [ ] Controls responsive
  - [ ] Feedback clear
  - [ ] Difficulty balanced
  - [ ] Progression smooth
  - [ ] Tutorial effective

- **Technical Polish**
  - [ ] Load times optimized
  - [ ] Memory usage controlled
  - [ ] Draw calls minimized
  - [ ] Texture streaming configured
  - [ ] Occlusion culling setup

## Phase 4: SHIP

### Goal
Deliver bug-free, platform-certified build.

### Quality Standards
- **Functionality**: Zero critical bugs
- **Performance**: Meets platform requirements
- **Visuals**: Consistent quality throughout
- **Code**: Production-ready, documented
- **Stability**: No crashes in normal play

### Acceptance Criteria
- [ ] All platform requirements met
- [ ] Certification tests passed
- [ ] Performance budgets achieved
- [ ] Accessibility features implemented
- [ ] Localization complete (if applicable)
- [ ] Age rating appropriate

### MCP Validation
```python
# Final build verification
save_level()
save_asset(asset_path="/Game/ProjectSettings", only_if_dirty=False)

# Asset dependency check
get_asset_dependencies(asset_path="/Game/Maps/MainLevel")

# Final screenshots for store
take_screenshot(filename="store_screenshot_1", show_ui=False, resolution=[1920, 1080])
```

### Ship Requirements
- **Zero Tolerance Issues**
  - No crashes in critical path
  - No progression blockers
  - No save corruption
  - No major visual artifacts
  - No placeholder content

- **Platform Compliance**
  - Controller support complete
  - Platform features integrated
  - Achievements/Trophies working
  - Online features stable
  - Storage requirements met

## Quality Gate Transitions

### Prototype → Development
Executive Producer must verify:
1. Core concept validated with user
2. Technical feasibility confirmed
3. Scope defined and agreed
4. Team structure planned

### Development → Polish
Executive Producer must verify:
1. All features implemented
2. No major technical debt
3. Performance baseline achieved
4. Art pipeline proven

### Polish → Ship
Executive Producer must verify:
1. Polish feedback incorporated
2. Performance targets met
3. Bug count acceptable
4. Certification requirements understood

## Per-Role Quality Expectations

### Blueprint Developer
- **Prototype**: Working logic
- **Development**: Clean graphs, proper events
- **Polish**: Optimized execution
- **Ship**: Zero compile errors

### Level Designer
- **Prototype**: Blocked out spaces
- **Development**: Proper metrics, flow
- **Polish**: Set dressed, lit
- **Ship**: Performance optimized

### Technical Artist
- **Prototype**: Basic shaders
- **Development**: Material pipeline
- **Polish**: Optimized shaders
- **Ship**: Platform-specific versions

## Automated Quality Checks

### Blueprint Validation
```python
# Check for compile errors
compile_blueprint(blueprint_name="MyBP")

# Verify node connections
find_blueprint_nodes(blueprint_name="MyBP", node_type="Event")
```

### Asset Validation
```python
# Check for missing references
get_asset_references(asset_path="/Game/MyAsset")

# Verify naming convention
list_assets(path="/Game", type_filter="StaticMesh")
```

### Performance Validation
```python
# Take performance screenshot
take_screenshot(filename="performance_stats", show_ui=True)

# Check actor count
actors = get_actors_in_level()
# Verify count is within budget
```

## Quality Communication

### Reporting Quality Issues
When reporting to Executive Producer:
```markdown
QUALITY ISSUE:
Phase: [Current phase]
Severity: [Critical/Major/Minor]
Area: [System affected]
Impact: [What this blocks]
Recommendation: [Suggested fix]
Time Estimate: [Fix duration]
```

### Quality Status Update
Regular quality reports should include:
```markdown
QUALITY STATUS:
Phase: [Current phase]
Overall: [Green/Yellow/Red]
- Functionality: [Status]
- Performance: [Status]
- Stability: [Status]
- Polish: [Status]
Next Gate: [Requirements to proceed]
```