# Agent Context Handoff Template

This template ensures consistent information transfer between the Executive Producer and specialized agents.

## Executive → Agent Handoff Format

```markdown
# CONTEXT
**Project**: [Project name and current phase]
**Vision**: [User's creative vision in 1-2 sentences]
**Current State**: [What has been done so far]
**Dependencies**: [What this work depends on or blocks]

# YOUR ROLE
You are a [specific role] specialist working on [project name].
Your expertise includes [specific skills].

# TASK
**Primary Objective**: [Clear, specific goal]
**Deliverables**:
1. [Specific deliverable 1]
2. [Specific deliverable 2]
3. [Specific deliverable 3]

**Success Criteria**:
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]

# CONSTRAINTS
**Technical**:
- Platform: [PC/Console/Mobile]
- Performance: [FPS target, memory budget]
- Engine Version: Unreal Engine 5.6

**Creative**:
- Art Style: [Realistic/Stylized/etc]
- Theme: [Sci-fi/Fantasy/etc]
- Mood: [Dark/Bright/etc]

**Time**: [Deadline or time estimate]

# ENVIRONMENT
**You are running in WSL2 on Windows**
- Unreal is running on Windows host
- Use MCP tools directly (NO Python scripts)
- Connection via port 55557

# CRITICAL COMMANDS
[Include relevant commands from wsl-commands.md]

# MCP REQUIREMENTS
1. Check /mcp status before starting
2. Use MCP tools only - NEVER write Python
3. If issues: /mcp restart and select UnrealMCP
4. Validate with take_screenshot after major changes

# VALIDATION
**How to verify your work**:
1. [Validation step 1]
2. [Validation step 2]
3. Take screenshot showing [specific view]

# REPORTING
**Report back with**:
- Status: [Completed/Blocked/In Progress]
- What was implemented
- Any issues encountered
- Screenshots of results
- Next recommended steps
```

## Agent → Executive Status Report Format

```markdown
# STATUS REPORT

## TASK
[Original task description]

## STATUS: [COMPLETED/BLOCKED/IN PROGRESS]

## IMPLEMENTATION
**What was done**:
- [Action taken 1]
- [Action taken 2]
- [Action taken 3]

**Technical Details**:
- [Important technical decision/detail]
- [Performance consideration]
- [Integration point]

## VALIDATION
- [✓] [Success criterion 1 met]
- [✓] [Success criterion 2 met]
- [ ] [Success criterion 3 status]

**Screenshots**: [Description of screenshots taken]

## ISSUES
**Blockers**: [Any blocking issues]
**Warnings**: [Potential problems]
**Decisions Needed**: [What needs user/executive input]

## NEXT STEPS
1. [Recommended next action]
2. [Follow-up task]
3. [Integration requirement]

## HANDOFF NOTES
[Any important context for next agent]
```

## Research Agent Context Template

```markdown
# RESEARCH TASK

## OBJECTIVE
Research [specific topic] for [project name]

## QUESTIONS TO ANSWER
1. [Specific question 1]
2. [Specific question 2]
3. [Specific question 3]

## SOURCES TO CHECK
- Unreal Engine 5.6 Documentation
- Epic Games Forums
- Recent GDC talks
- Community best practices
- Similar shipped games

## DELIVERABLES
- Current best practices for [topic]
- Performance considerations
- Example implementations
- Recommended approach

## USE TOOLS
- WebSearch for latest information
- WebFetch for documentation pages
- Compile findings in structured format
```

## Quick Task Templates

### Blueprint Task
```markdown
QUICK TASK: Create [Blueprint name]
TYPE: Blueprint Development
PARENT: [Parent class]
COMPONENTS: [List components needed]
FUNCTIONALITY: [Core behavior]
VALIDATION: Compile and spawn in level
```

### Level Design Task
```markdown
QUICK TASK: Build [area/level name]
TYPE: Level Design
THEME: [Visual theme]
SIZE: [Dimensions or scope]
ELEMENTS: [Key elements to include]
VALIDATION: Screenshot from multiple angles
```

### Optimization Task
```markdown
QUICK TASK: Optimize [system/area]
TYPE: Performance
TARGET: [FPS/memory target]
CURRENT: [Current performance]
SCOPE: [What to optimize]
VALIDATION: Performance metrics before/after
```

## Information Preservation

### Project State File
Each project should maintain a state file with:
```markdown
# PROJECT: [Name]
## Vision
[User's original vision]

## Current Phase
[Prototype/Development/Polish/Ship]

## Completed Work
- [Completed feature 1]
- [Completed feature 2]

## Active Tasks
- [In progress task 1]
- [In progress task 2]

## Pending Tasks
- [Queued task 1]
- [Queued task 2]

## Technical Decisions
- [Decision 1 and rationale]
- [Decision 2 and rationale]

## Known Issues
- [Issue 1 and workaround]
- [Issue 2 and status]
```

## Communication Patterns

### Parallel Work Handoff
When tasks can run simultaneously:
```markdown
PARALLEL TASKS:
Task A: [Independent task 1] → Agent unreal-dev00
Task B: [Independent task 2] → Agent unreal-dev01
Task C: [Independent task 3] → Agent unreal-dev02

No dependencies between A, B, C
Merge results after completion
```

### Sequential Work Handoff
When tasks depend on each other:
```markdown
SEQUENTIAL PIPELINE:
Step 1: [Foundation task] → Agent unreal-dev00
  ↓ Output: [What's produced]
Step 2: [Dependent task] → Agent unreal-dev01
  ↓ Output: [What's produced]
Step 3: [Final task] → Agent unreal-dev02
```

### Specialist Consultation
When specific expertise needed:
```markdown
CONSULTATION REQUEST:
Issue: [Problem description]
Context: [Relevant background]
Question: [Specific question]
Constraints: [Any limitations]
Need: [Expert recommendation]
```

## Quality Gates Integration

For each phase, include appropriate quality standards:

### Prototype Phase
- Core mechanics functional
- Basic interactions work
- Proof of concept achieved

### Development Phase
- Systems properly architected
- Code follows conventions
- Features fully implemented

### Polish Phase
- Performance optimized
- Assets finalized
- User experience refined

### Ship Phase
- No critical bugs
- All platforms tested
- Documentation complete