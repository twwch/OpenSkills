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
- **Sandbox execution** - Secure script execution in isolated AIO Sandbox environment
- **Automatic file sync** - Upload input files and download outputs automatically

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
    # Create agent with infographic-skills
    agent = await create_agent(
        skill_paths=["./infographic-skills"],
        api_key="your-api-key",
        model="gpt-4",
    )

    # Chat with automatic skill invocation
    response = await agent.chat("帮我总结会议")
    print(response.content)
    print(f"Used skill: {response.skill_used}")

asyncio.run(main())
```

### Using Sandbox Mode (Recommended for Script Execution)

```python
import asyncio
from openskills import create_agent

async def main():
    # Create agent with sandbox enabled
    agent = await create_agent(
        skill_paths=["./skills"],
        api_key="your-api-key",
        model="gpt-4",
        use_sandbox=True,  # Enable sandbox execution
        sandbox_base_url="http://localhost:8080",
        auto_execute_scripts=True,
    )

    # Local file paths are automatically uploaded to sandbox
    response = await agent.chat("请处理这个文件: /path/to/file.pdf")
    print(response.content)

    # Output files are automatically downloaded to skill_dir/output/

asyncio.run(main())
```

### Using SkillManager (Low-level API)

```python
from pathlib import Path
from openskills import SkillManager

manager = SkillManager([Path("./infographic-skills")])

# Discover infographic-skills (Layer 1 - Metadata)
await manager.discover()

# Match user query
skills = manager.match("summarize meeting")

# Load instruction (Layer 2)
if skills:
    instruction = await manager.load_instruction(skills[0].name)
    print(instruction.content)
```

## Sandbox Environment

OpenSkills supports executing scripts in an isolated sandbox environment using [AIO Sandbox](https://github.com/agent-infra/aio-sandbox). This provides:

- **Security**: Scripts run in isolated containers
- **Dependency management**: Auto-install Python packages defined in SKILL.md
- **File synchronization**: Automatic upload/download of files

### Installing AIO Sandbox

#### Option 1: Docker (Recommended)

```bash
# Pull and run the sandbox container
docker run -d --name aio-sandbox \
  -p 8080:8080 \
  ghcr.io/agent-infra/aio-sandbox:latest

# Verify it's running
curl http://localhost:8080/health
```

#### Option 2: Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  sandbox:
    image: ghcr.io/agent-infra/aio-sandbox:latest
    ports:
      - "8080:8080"
    volumes:
      - sandbox-data:/home/gem
    restart: unless-stopped

volumes:
  sandbox-data:
```

```bash
docker-compose up -d
```

### Sandbox Features

#### Automatic Dependency Installation

Define dependencies in SKILL.md frontmatter:

```yaml
dependency:
  python:
    - PyMuPDF==1.23.8
    - pandas>=2.0.0
  system:
    - mkdir -p output/images
```

Dependencies are installed automatically when the skill is initialized.

#### Automatic File Synchronization

1. **Upload**: Local file paths in script input are auto-uploaded to `/home/gem/uploads/`
2. **Download**: Specify output directories in script config to auto-download results

```yaml
scripts:
  - name: process_file
    path: scripts/process.py
    description: Process uploaded files
    timeout: 120
    outputs:
      - /home/gem/output  # Auto-sync to local skill_dir/output/
```

#### Sandbox Client API

For advanced use cases, use the SandboxClient directly:

```python
from openskills.sandbox import SandboxClient

async with SandboxClient("http://localhost:8080") as client:
    # Execute commands
    result = await client.exec_command("python --version")
    print(result.output)

    # File operations
    await client.write_file("/home/gem/test.txt", "Hello World")
    content = await client.read_file("/home/gem/test.txt")

    # Upload/download files
    await client.upload_file(local_bytes, "/home/gem/uploads/file.pdf")
    data = await client.download_file("/home/gem/output/result.txt")

    # List files
    files = await client.list_files("/home/gem/output")
    for f in files:
        print(f"{f.name} (dir={f.is_dir})")
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
    skill_paths=["./infographic-skills"],
    llm_client=client,
)
```

## Examples

See the [examples](./examples) directory for complete examples:

- `demo.py` - Main demo showing reference auto-discovery and LLM selection
- `prompt-optimizer/` - Prompt engineering skill with 57 frameworks (auto-discovered)
- `meeting-summary/` - Meeting summarization skill with finance reference
- `office-skills/` - Word and Excel processing skills
- `file-to-article-generator/` - PDF/Word parsing with sandbox execution
- `weekly-report-to-annual/` - Weekly report aggregation skill

### Running Examples

#### Basic Demo (Local Execution)
```bash
cd examples
export OPENAI_API_KEY=your-api-key
python demo.py
```

#### Sandbox Demo (Recommended)
```bash
# 1. Start sandbox first
docker run -d -p 8080:8080 ghcr.io/agent-infra/aio-sandbox:latest

# 2. Run demo with sandbox
cd examples/file-to-article-generator
export OPENAI_API_KEY=your-api-key
python demo.py /path/to/your/file.pdf
```

The sandbox demo will:
1. Initialize sandbox environment and install dependencies
2. Upload your file to sandbox automatically
3. Execute parsing script in isolated environment
4. Download generated images to local `output/` directory
5. Generate article with proper image references

## CLI Commands

```bash
# List all infographic-skills
openskills list

# Show skill details
openskills show meeting-summary

# Validate a skill
openskills validate ./my-skill/

# Match query to infographic-skills
openskills match "summarize meeting"
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
