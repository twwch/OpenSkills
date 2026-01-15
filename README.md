# OpenSkills

An open-source Agent Skill framework implementing the progressive disclosure architecture for AI agent skills.

## Features

- **Three-layer progressive disclosure architecture**
  - Layer 1 (Metadata): Always loaded for skill discovery
  - Layer 2 (Instruction): Loaded on demand when skill is selected
  - Layer 3 (Resources): Conditionally loaded References and Scripts

- **SKILL.md file format** - Simple markdown-based skill definition
- **Reference support** - Conditionally load additional documents
- **Script execution** - Run scripts with sandboxing
- **LLM integration** - OpenAI-compatible API support
- **CLI tools** - Command-line interface for skill management

## Installation

```bash
pip install openskills
```

## Quick Start

### Create a Skill

```bash
openskills init --name my-skill --description "My custom skill"
```

### SKILL.md Format

```markdown
---
name: meeting-summary
description: Summarize meetings in structured format
version: 1.0.0
triggers:
  - "summarize meeting"
  - "会议总结"
references:
  - path: ./handbook.md
    condition: "When content involves finance"
scripts:
  - name: upload
    path: ./upload.py
    description: Upload summary to cloud
---

# Meeting Summary

Instructions for the skill...
```

### Use in Python

```python
from openskills import SkillManager

manager = SkillManager([Path("~/.openskills/skills")])

# Discover skills (Layer 1)
await manager.discover()

# Match user query
skills = manager.match("summarize meeting")

# Load instruction (Layer 2)
if skills:
    await manager.load_instruction(skills[0].name)
```

### CLI Commands

```bash
# List all skills
openskills list

# Show skill details
openskills show meeting-summary

# Validate a skill
openskills validate ./my-skill/

# Match query to skills
openskills match "summarize meeting"
```

## Architecture

```
┌─────────────────────────────────────────┐
│  Layer 1: Metadata (Always Loaded)      │
│  - name, description, triggers          │
├─────────────────────────────────────────┤
│  Layer 2: Instruction (On Demand)       │
│  - SKILL.md body content                │
├─────────────────────────────────────────┤
│  Layer 3: Resources (Conditional)       │
│  - References (read)                    │
│  - Scripts (execute)                    │
└─────────────────────────────────────────┘
```

## License

MIT
