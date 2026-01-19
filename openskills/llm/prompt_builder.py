"""
Prompt Builder - Constructs prompts for skill-enhanced LLM interactions.

Handles the integration of skill instructions and resources into
the LLM conversation.
"""

from openskills.core.skill import Skill
from openskills.models.metadata import SkillMetadata


class PromptBuilder:
    """
    Builds prompts for skill-enhanced LLM interactions.

    Implements the progressive disclosure pattern by constructing
    prompts that include only the necessary information at each stage.
    """

    SKILL_CATALOG_TEMPLATE = """## Available Skills

You have access to the following infographic-skills. When the user's request matches a skill, you should use it.

{skills_list}

To use a skill, indicate which skill you want to use and I will provide the detailed instructions.
"""

    SKILL_ACTIVE_TEMPLATE = """## Active Skill: {name}

{instruction}
"""

    SCRIPT_AVAILABLE_TEMPLATE = """
## Available Actions

You can invoke the following scripts when needed:

{scripts_list}

To invoke a script, use the format: `[INVOKE:{{script_name}}]` with any required parameters.
"""

    def __init__(self):
        pass

    def build_skill_catalog(self, metadata_list: list[SkillMetadata]) -> str:
        """
        Build a skill catalog prompt (Layer 1).

        This is used to show the LLM what infographic-skills are available
        without loading all their instructions.

        Args:
            metadata_list: List of skill metadata

        Returns:
            Formatted skill catalog prompt
        """
        if not metadata_list:
            return ""

        skills_lines = []
        for meta in metadata_list:
            triggers = ", ".join(meta.triggers) if meta.triggers else "N/A"
            skills_lines.append(
                f"- **{meta.name}**: {meta.description}\n"
                f"  Triggers: {triggers}"
            )

        skills_list = "\n".join(skills_lines)
        return self.SKILL_CATALOG_TEMPLATE.format(skills_list=skills_list)

    def build_active_skill_prompt(
        self,
        skill: Skill,
        include_scripts: bool = True,
        include_references: bool = True,
    ) -> str:
        """
        Build a prompt for an active skill (Layer 2+3).

        Args:
            skill: The active skill
            include_scripts: Whether to include script hints
            include_references: Whether to include loaded references

        Returns:
            Formatted skill prompt
        """
        parts = []

        # Add instruction content
        if skill.instruction:
            parts.append(self.SKILL_ACTIVE_TEMPLATE.format(
                name=skill.name,
                instruction=skill.instruction.content,
            ))
        else:
            parts.append(f"## Active Skill: {skill.name}\n\n{skill.description}")

        # Add script hints
        if include_scripts and skill.scripts:
            scripts_lines = []
            for script in skill.scripts:
                scripts_lines.append(f"- `{script.name}`: {script.description}")
            scripts_list = "\n".join(scripts_lines)
            parts.append(self.SCRIPT_AVAILABLE_TEMPLATE.format(scripts_list=scripts_list))

        # Add loaded references
        if include_references:
            for ref in skill.references:
                if ref.is_loaded() and ref.content:
                    parts.append(f"\n## Reference: {ref.path}\n\n{ref.content}")

        return "\n".join(parts)

    def build_system_prompt(
        self,
        base_prompt: str | None = None,
        skill_catalog: list[SkillMetadata] | None = None,
        active_skill: Skill | None = None,
    ) -> str:
        """
        Build a complete system prompt.

        Args:
            base_prompt: Base system prompt
            skill_catalog: Available infographic-skills for discovery
            active_skill: Currently active skill

        Returns:
            Complete system prompt
        """
        parts = []

        if base_prompt:
            parts.append(base_prompt)

        if active_skill:
            # If a skill is active, include its full instructions
            parts.append(self.build_active_skill_prompt(active_skill))
        elif skill_catalog:
            # Otherwise, show the skill catalog
            parts.append(self.build_skill_catalog(skill_catalog))

        return "\n\n".join(parts)

    def extract_script_invocations(self, text: str) -> list[tuple[str, str]]:
        """
        Extract script invocation requests from LLM output.

        Looks for patterns like: [INVOKE:script_name] or [INVOKE:script_name(args)]

        Args:
            text: LLM output text

        Returns:
            List of (script_name, args) tuples
        """
        import re

        invocations = []

        # Pattern: [INVOKE:name] or [INVOKE:name(args)]
        pattern = r"\[INVOKE:(\w+)(?:\((.*?)\))?\]"
        matches = re.findall(pattern, text)

        for name, args in matches:
            invocations.append((name, args or ""))

        return invocations

    def format_script_result(self, script_name: str, result: str) -> str:
        """
        Format a script execution result for inclusion in conversation.

        Args:
            script_name: Name of the executed script
            result: Script output

        Returns:
            Formatted result message
        """
        return f"## Script Result: {script_name}\n\n```\n{result}\n```"
