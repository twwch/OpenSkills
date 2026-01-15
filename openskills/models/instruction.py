"""
Skill instruction model - Layer 2 (Loaded on demand).

The instruction layer contains the actual rules and guidelines for the skill.
This is loaded only when a skill is selected for use.
"""

from pydantic import BaseModel, Field


class SkillInstruction(BaseModel):
    """
    Second layer: Instruction (loaded on demand).

    Contains the full instruction content from SKILL.md body.
    This is injected into the LLM's system prompt when the skill is active.
    """

    content: str = Field(
        ...,
        description="The markdown content of the skill instructions",
    )

    raw_content: str = Field(
        default="",
        description="Original raw content including frontmatter",
    )

    def get_system_prompt(self) -> str:
        """
        Get the instruction content formatted for use as a system prompt.

        Returns:
            The instruction content ready for LLM injection
        """
        return self.content.strip()

    def get_token_estimate(self) -> int:
        """
        Estimate the number of tokens in the instruction.

        Uses a rough estimate of 4 characters per token.

        Returns:
            Estimated token count
        """
        return len(self.content) // 4
