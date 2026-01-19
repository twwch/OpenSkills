"""
OpenSkills - An open-source Agent Skill framework.

Implements the progressive disclosure architecture for AI agent infographic-skills,
compatible with Claude Code's skill system.

Quick Start:
    from openskills import create_agent

    # Create and initialize agent
    agent = await create_agent(
        skill_paths=["~/.openskills/infographic-skills"],
        model="gpt-4",
    )

    # Chat with automatic skill invocation
    response = await agent.chat("帮我总结一下今天的会议")
    print(response.content)
"""

from openskills.core.manager import SkillManager
from openskills.core.skill import Skill
from openskills.models.metadata import SkillMetadata
from openskills.models.instruction import SkillInstruction
from openskills.models.resource import Reference, Script
from openskills.agent import SkillAgent, create_agent, AgentResponse
from openskills.llm.openai_compat import OpenAICompatClient, AzureOpenAIClient, create_client

try:
    from openskills._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"
__all__ = [
    # Core
    "SkillManager",
    "Skill",
    "SkillMetadata",
    "SkillInstruction",
    "Reference",
    "Script",
    # Agent
    "SkillAgent",
    "create_agent",
    "AgentResponse",
    # LLM Clients
    "OpenAICompatClient",
    "AzureOpenAIClient",
    "create_client",
]
