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
- **Smart Reference loading** - Three modes (explicit/implicit/always) with LLM-based selection
- **Auto-discovery** - Automatically discover references from `references/` directory
- **Script execution** - Run scripts triggered by LLM via `[INVOKE:name]`
- **Multiple LLM providers** - OpenAI, Azure OpenAI, Ollama, Together, Groq, DeepSeek
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
    mode: explicit  # LLM evaluates condition
  - path: references/frameworks/
    mode: implicit  # LLM decides if useful (default)
  - path: references/safety-policy.md
    mode: always    # Always loaded

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

## Reference Loading Modes

References support three loading modes:

| Mode | Behavior |
|------|----------|
| `explicit` | Has condition, LLM evaluates whether condition is met |
| `implicit` | No condition, LLM decides if useful for current query (default) |
| `always` | Always loaded (e.g., safety guidelines, specs) |

### Auto-Discovery

References are **automatically discovered** from the `references/` directory. You don't need to declare every file in frontmatter:

```
my-skill/
├── SKILL.md
└── references/
    ├── guide.md          # Auto-discovered (implicit mode)
    ├── api-docs.md       # Auto-discovered (implicit mode)
    └── frameworks/
        └── react.md      # Auto-discovered (implicit mode)
```

You can still declare specific references in frontmatter to customize their behavior:

```yaml
references:
  # Override mode for specific file
  - path: references/guide.md
    mode: always  # Now always loaded instead of implicit

  # Add condition for another file
  - path: references/api-docs.md
    condition: "When user asks about API"
    mode: explicit
```

Auto-discovered files that aren't declared in frontmatter default to `implicit` mode, letting the LLM decide whether to load them based on the user's query.

## Environment Variables

### OpenAI
```bash
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
export OPENAI_MODEL=gpt-4  # Optional
```

### Azure OpenAI
```bash
export AZURE_OPENAI_API_KEY=your-azure-api-key
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
export AZURE_OPENAI_DEPLOYMENT=your-deployment-name
export AZURE_OPENAI_API_VERSION=2024-02-15-preview  # Optional
```

### Using Azure OpenAI

```python
from openskills import AzureOpenAIClient, SkillAgent

# Method 1: Using environment variables
client = AzureOpenAIClient()

# Method 2: Explicit configuration
client = AzureOpenAIClient(
    api_key="your-api-key",
    endpoint="https://your-resource.openai.azure.com",
    deployment="gpt-4",
)

# Method 3: Using create_client helper
from openskills import create_client
client = create_client("azure", deployment="gpt-4")

# Use with SkillAgent
agent = SkillAgent(
    skill_paths=["./skills"],
    llm_client=client,
)
```

## Examples

See the [examples](./examples) directory for complete examples:

- `demo.py` - Main demo showing reference auto-discovery and LLM selection
- `prompt-optimizer/` - Prompt engineering skill with 57 frameworks (auto-discovered)
- `meeting-summary/` - Meeting summarization skill with finance reference
- `office-skills/` - Word and Excel processing skills

Run the demo:
```bash
cd examples
python demo.py
```

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
