# Agent Knowledge Library System

## How Claude Code Agents Work

Claude Code agents are defined as markdown files with YAML frontmatter in `.claude/agents/`. The system reads these files when you use the Task tool with a specific `subagent_type`.

## Current Structure
```
.claude/agents/
├── core/                 # Specialized agents
│   ├── blueprint-developer.md
│   └── level-designer.md
├── shared/              # Shared knowledge (currently unused)
│   ├── ue5-naming-conventions.md
│   ├── project-organization.md
│   ├── blueprint-standards.md
│   └── ...
└── unreal-engine-expert.md  # Main orchestrator
```

## Implementation Strategy

### Option 1: Include References in Agent Instructions (RECOMMENDED)
Since agents are self-contained markdown files, include explicit references to shared knowledge:

```markdown
---
name: blueprint-developer
description: Blueprint development specialist
model: sonnet
---

# Blueprint Developer Agent

## Core Knowledge Base
This agent follows the standards defined in:
- **Naming Conventions**: See `.claude/agents/shared/ue5-naming-conventions.md`
- **Blueprint Standards**: See `.claude/agents/shared/blueprint-standards.md`
- **Project Organization**: See `.claude/agents/shared/project-organization.md`

When working on blueprints, I reference these documents for:
1. Asset naming (BP_, WBP_, ABP_ prefixes)
2. Code organization patterns
3. Quality standards

[Rest of agent instructions...]
```

### Option 2: Create a Knowledge Loader Agent
Create a specialized agent that other agents can invoke to load knowledge:

```markdown
---
name: knowledge-librarian
description: Provides shared knowledge and standards to other agents
---

# Knowledge Librarian

I maintain and provide access to shared knowledge. When asked, I read and summarize:
- Naming conventions
- Coding standards
- Best practices
- Project organization

Other agents can ask me for specific knowledge before starting tasks.
```

### Option 3: Embed Knowledge Directly (Simple but Redundant)
Copy the essential parts of shared knowledge directly into each agent's instructions. This ensures agents always have the information but creates maintenance overhead.

## Recommended Implementation Plan

1. **Update Agent Templates** to include knowledge references
2. **Create a Knowledge Index** listing all available shared resources
3. **Add Knowledge Validation** - agents check if they're following standards
4. **Create Examples** showing how to apply the knowledge

## How to Use Shared Knowledge in Agents

### In Agent Instructions:
```markdown
## Applying Standards

Before creating any asset, I check:
1. Read naming conventions from shared/ue5-naming-conventions.md
2. Verify against blueprint standards in shared/blueprint-standards.md
3. Follow project organization from shared/project-organization.md

Example workflow:
- Creating a player controller blueprint
- Check: BP_ prefix required (from naming conventions)
- Location: /Game/Blueprints/Player/ (from project organization)
- Result: BP_PlayerController in correct folder
```

### During Execution:
Agents should explicitly mention when applying standards:
```
"Following UE5 naming conventions, I'll name this BP_PlayerCharacter"
"Per project organization standards, placing in /Game/Blueprints/Characters/"
```

## Benefits of This System

1. **Consistency** - All agents follow same standards
2. **Maintainability** - Update knowledge in one place
3. **Transparency** - Users see which standards are applied
4. **Flexibility** - Agents can adapt knowledge to context
5. **Education** - Agents teach standards while working

## Next Steps

1. Update each agent to reference shared knowledge
2. Create knowledge validation checklist
3. Add examples of applied standards
4. Test with real development tasks