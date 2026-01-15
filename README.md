# OpenSkills SDK

An open-source Agent Skill framework implementing the progressive disclosure architecture for AI agent skills.

[![PyPI version](https://badge.fury.io/py/openskills-sdk.svg)](https://badge.fury.io/py/openskills-sdk)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- **Three-layer progressive disclosure architecture**
  - Layer 1 (Metadata): Always loaded for skill discovery
  - Layer 2 (Instruction): Loaded on demand when skill is selected
  - Layer 3 (Resources): Conditionally loaded References and Scripts

- **SKILL.md file format** - Simple markdown-based skill definition
- **Reference support** - Conditionally load additional documents
- **Script execution** - Run scripts triggered by LLM
- **LLM integration** - OpenAI-compatible API support with streaming
- **Auto skill invocation** - Automatically match and invoke skills based on user queries
- **Multimodal support** - Handle images via URL, base64, or file path

## Installation

```bash
pip install openskills-sdk
```

## Quick Start

### Using SkillAgent (Recommended)

```python
import asyncio
from openskills import create_agent

async def main():
    # Create agent with skills
    agent = await create_agent(
        skill_paths=["./skills"],
        api_key="your-api-key",
        model="gpt-4",
    )

    # Chat with automatic skill invocation
    response = await agent.chat("帮我总结会议")
    print(response.content)
    print(f"Used skill: {response.skill_used}")

asyncio.run(main())
```

### Using SkillManager (Low-level API)

```python
from pathlib import Path
from openskills import SkillManager

manager = SkillManager([Path("./skills")])

# Discover skills (Layer 1 - Metadata)
await manager.discover()

# Match user query
skills = manager.match("summarize meeting")

# Load instruction (Layer 2)
if skills:
    instruction = await manager.load_instruction(skills[0].name)
    print(instruction.content)
```

## Skill Structure

```
my-skill/
├── SKILL.md              # Skill definition (required)
├── references/           # Reference documents
│   └── handbook.md
└── scripts/              # Executable scripts
    └── upload.py
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
  - path: references/finance-handbook.md
    condition: "When content involves finance or budget"
    description: Financial guidelines

scripts:
  - name: upload
    path: scripts/upload.py
    description: Upload summary to cloud storage
---

# Meeting Summary Skill

You are a professional meeting assistant...

## Output Format

...
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenSkills SDK                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Metadata (Always loaded)                          │
│  ├── name, description, triggers, tags                      │
│  └── Used for skill discovery and matching                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Instruction (On-demand)                           │
│  ├── SKILL.md body content                                  │
│  └── Loaded when skill is selected                          │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Resources (Conditional)                           │
│  ├── Reference: Documents loaded based on conditions        │
│  └── Script: Executed when LLM outputs [INVOKE:name]        │
└─────────────────────────────────────────────────────────────┘
```

## Environment Variables

```bash
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
export OPENAI_MODEL=gpt-4  # Optional
```

## Examples

See the [examples](./examples) directory for complete examples:

- `meeting-summary/` - Meeting summarization skill with finance reference
- `office-skills/` - Word and Excel processing skills

## CLI Commands

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

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
