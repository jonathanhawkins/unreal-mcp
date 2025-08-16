# Agent Communication Protocols

This document defines how agents communicate with each other, the Executive Producer, and the user.

## Communication Hierarchy

```
User (Creative Director)
    ↕️
Executive Producer (Orchestrator)
    ↕️
Research Agents | Development Agents | Specialist Agents
```

## Tmux Session Naming Convention

### Session Types
- `unreal-exec` - Executive Producer session
- `unreal-research-XX` - Research agents (00, 01, 02...)
- `unreal-dev-XX` - Development agents (00, 01, 02...)
- `unreal-spec-XX` - Specialist agents (00, 01, 02...)

### Examples
```bash
tmux new -s unreal-exec        # Executive Producer
tmux new -s unreal-research-00  # First research agent
tmux new -s unreal-dev-00       # First dev agent
tmux new -s unreal-spec-00      # First specialist
```

## Inter-Agent Communication

### Direct Communication Methods

#### 1. File-Based Communication
Agents share information through files:
```bash
# Agent A writes status
echo "TASK_COMPLETE: Blueprint compiled" > /tmp/unreal-status-dev00.txt

# Agent B reads status
cat /tmp/unreal-status-dev00.txt
```

#### 2. Tmux Pane Monitoring
Executive monitors agent output:
```bash
# Executive checks agent progress
tmux capture-pane -t unreal-dev-00 -p -S -100
```

#### 3. MCP Shared State
Agents verify each other's work:
```python
# Agent A creates actor
spawn_actor(name="SharedObject", type="StaticMeshActor", location=[0,0,0])

# Agent B modifies it
set_actor_property(name="SharedObject", property_name="Material", property_value="MI_Gold")
```

## Communication Protocols

### 1. Task Assignment Protocol

Executive → Agent:
```markdown
=== TASK ASSIGNMENT ===
TO: unreal-dev-00
TASK_ID: TASK_001
PRIORITY: HIGH
DEADLINE: 30 minutes

TASK: Implement player movement system
DEPENDENCIES: None
BLOCKS: TASK_002, TASK_003

BEGIN WORK IMMEDIATELY
======================
```

### 2. Status Update Protocol

Agent → Executive:
```markdown
=== STATUS UPDATE ===
FROM: unreal-dev-00
TASK_ID: TASK_001
STATUS: IN_PROGRESS
PROGRESS: 60%

COMPLETED:
- Basic movement implemented
- Jump mechanics working

REMAINING:
- Double jump
- Wall slide

BLOCKERS: None
ETA: 10 minutes
===================
```

### 3. Completion Protocol

Agent → Executive:
```markdown
=== TASK COMPLETE ===
FROM: unreal-dev-00
TASK_ID: TASK_001
STATUS: COMPLETED
TIME_TAKEN: 25 minutes

DELIVERABLES:
- PlayerMovementBP created
- All mechanics implemented
- Screenshot: player_movement_demo.png

VALIDATION:
- [✓] Tested in editor
- [✓] No compile errors
- [✓] Performance acceptable

HANDOFF_NOTES:
- Ready for animation integration
- Input mappings created
====================
```

### 4. Blocker Protocol

Agent → Executive:
```markdown
=== BLOCKER ALERT ===
FROM: unreal-dev-01
TASK_ID: TASK_002
SEVERITY: CRITICAL

ISSUE: Cannot access PlayerMovementBP
REASON: File locked by another process
IMPACT: Cannot proceed with animation

NEEDS:
- Executive intervention
- OR: Alternative approach approval

WAITING FOR RESPONSE
====================
```

### 5. Research Request Protocol

Executive → Research Agent:
```markdown
=== RESEARCH REQUEST ===
TO: unreal-research-00
REQUEST_ID: RES_001
URGENCY: MEDIUM

TOPIC: Best practices for character wall-running in UE5.6

QUESTIONS:
1. Latest implementation techniques
2. Performance considerations
3. Common pitfalls

SOURCES:
- Official UE5.6 docs
- Recent GDC talks
- Community forums

DELIVER TO: unreal-dev-00
DEADLINE: 15 minutes
======================
```

### 6. Research Delivery Protocol

Research Agent → Dev Agent:
```markdown
=== RESEARCH FINDINGS ===
FROM: unreal-research-00
TO: unreal-dev-00
REQUEST_ID: RES_001

TOPIC: Wall-running implementation

KEY FINDINGS:
1. Use Character Movement Component
2. Custom movement mode recommended
3. Trace for wall normals

BEST PRACTICES:
- Cache wall normals
- Use prediction for networking
- Limit wall angle to 15 degrees

RESOURCES:
- [Link to documentation]
- [Example project reference]

RECOMMENDATION:
Implement as custom movement mode
======================
```

## Synchronization Protocols

### Parallel Work Coordination
When agents work in parallel:
```markdown
=== PARALLEL WORK START ===
AGENTS: unreal-dev-00, unreal-dev-01, unreal-dev-02
SYNC_POINT: 14:30
MERGE_STRATEGY: Executive review

ASSIGNMENTS:
- dev-00: Player mechanics
- dev-01: Enemy AI
- dev-02: Level geometry

NO SHARED DEPENDENCIES
========================
```

### Sequential Work Handoff
When work must be sequential:
```markdown
=== HANDOFF PROTOCOL ===
FROM: unreal-dev-00
TO: unreal-dev-01
HANDOFF_ID: HAND_001

COMPLETED WORK:
- Base character Blueprint
- Movement component configured

NEXT PHASE:
- Add animation blueprint
- Connect animation events

FILES MODIFIED:
- /Game/Blueprints/BP_PlayerCharacter
- /Game/Input/IA_PlayerInput

VALIDATION COMPLETE
====================
```

## Emergency Protocols

### Critical Error Protocol
```markdown
=== CRITICAL ERROR ===
FROM: unreal-dev-00
SEVERITY: CRITICAL
AUTO_ESCALATE: YES

ERROR: Unreal Engine crashed
IMPACT: All work stopped
DATA_LOSS: Minimal (auto-save 5 min ago)

RECOVERY PLAN:
1. Restart Unreal Engine
2. Verify MCP connection
3. Resume from last save

EXECUTIVE ACTION REQUIRED
======================
```

### Rollback Protocol
```markdown
=== ROLLBACK REQUEST ===
FROM: unreal-spec-00
REASON: Performance regression
ROLLBACK_TO: Commit abc123

AFFECTED_FILES:
- BP_GameMode
- BP_PlayerController

APPROVAL_NEEDED: Executive
=====================
```

## Communication Shortcuts

### Quick Status Codes
Agents can use codes for common statuses:
- `[WIP]` - Work in progress
- `[BLOCKED]` - Blocked, need help
- `[READY]` - Ready for review
- `[DONE]` - Task complete
- `[HELP]` - Need assistance
- `[WAIT]` - Waiting for dependency

### Priority Levels
- `P0` - Critical, block everything
- `P1` - High, do immediately
- `P2` - Medium, do soon
- `P3` - Low, when time permits

## Monitoring Commands

### Executive Monitoring Suite
```bash
# Check all agent statuses
for session in $(tmux ls | grep unreal- | cut -d: -f1); do
    echo "=== $session ==="
    tmux capture-pane -t $session -p -S -10
done

# Monitor specific agent
watch -n 5 'tmux capture-pane -t unreal-dev-00 -p -S -20'

# Check for blockers
grep -r "BLOCKED" /tmp/unreal-status-*.txt
```

### Agent Self-Reporting
```bash
# Agent reports status
echo "[READY] Task 001 complete" > /tmp/unreal-status-dev00.txt

# Agent checks for new tasks
cat /tmp/unreal-tasks-dev00.txt
```

## Best Practices

### DO:
- ✅ Use clear, structured messages
- ✅ Include task IDs for tracking
- ✅ Report blockers immediately
- ✅ Validate before marking complete
- ✅ Document handoff requirements
- ✅ Use status codes consistently

### DON'T:
- ❌ Skip status updates
- ❌ Work on wrong priorities
- ❌ Assume context is known
- ❌ Forget validation steps
- ❌ Leave sessions unnamed
- ❌ Ignore blockers

## Communication Templates

### Quick Templates for Common Messages

#### Request Help
```
[HELP] Task: {task_id} Issue: {description} Need: {what_you_need}
```

#### Report Progress
```
[WIP] Task: {task_id} Progress: {percent}% ETA: {time}
```

#### Mark Complete
```
[DONE] Task: {task_id} Validation: PASS Next: {next_task}
```

#### Report Blocker
```
[BLOCKED] Task: {task_id} Reason: {why} Impact: {what_it_affects}
```

## Session Lifecycle

### Starting Session
```markdown
=== SESSION START ===
AGENT: unreal-dev-00
TYPE: Blueprint Developer
MCP: Connected
UNREAL: Running
READY FOR TASKS
==================
```

### Ending Session
```markdown
=== SESSION END ===
AGENT: unreal-dev-00
TASKS_COMPLETED: 5
TASKS_PENDING: 2
HANDOFF: See /tmp/unreal-handoff-dev00.md
SESSION TERMINATED
==================
```