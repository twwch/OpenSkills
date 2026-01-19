"""
SkillAgent - Automatic skill invocation for LLM conversations.

This module provides an agent that automatically:
1. Discovers and loads infographic-skills from specified directories
2. Matches user queries to appropriate infographic-skills
3. Injects skill instructions into LLM prompts
4. Handles conditional loading of references
5. Executes scripts when requested by the LLM
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import AsyncIterator, Callable

from openskills.core.manager import SkillManager
from openskills.core.skill import Skill
from openskills.llm.base import (
    BaseLLMClient,
    Message,
    ChatResponse,
    StreamChunk,
    ImageContent,
)
from openskills.llm.prompt_builder import PromptBuilder
from openskills.models.resource import ReferenceMode


class AgentState(str, Enum):
    """Agent state in the conversation."""
    IDLE = "idle"  # No skill active
    SKILL_ACTIVE = "skill_active"  # A skill is currently active
    AWAITING_CONFIRMATION = "awaiting_confirmation"  # Waiting for user to confirm skill


@dataclass
class ConversationContext:
    """Context for the current conversation."""
    messages: list[Message] = field(default_factory=list)
    active_skill: Skill | None = None
    state: AgentState = AgentState.IDLE
    loaded_references: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from the agent."""
    content: str
    skill_used: str | None = None
    references_loaded: list[str] = field(default_factory=list)
    scripts_executed: list[str] = field(default_factory=list)
    usage: dict = field(default_factory=dict)


class SkillAgent:
    """
    Agent that automatically invokes infographic-skills based on user queries.

    Usage:
        agent = SkillAgent(
            skill_paths=[Path("~/.openskills/infographic-skills"), Path("./.infographic-skills")],
            llm_client=OpenAICompatClient(model="gpt-4"),
        )

        # Initialize (discover infographic-skills)
        await agent.initialize()

        # Chat with automatic skill invocation
        response = await agent.chat("帮我总结一下今天的会议")
        print(response.content)
        print(f"Used skill: {response.skill_used}")

        # Streaming
        async for chunk in agent.chat_stream("分析这张图片", images=[...]):
            print(chunk, end="")
    """

    def __init__(
        self,
        skill_paths: list[Path],
        llm_client: BaseLLMClient,
        base_system_prompt: str | None = None,
        auto_select_skill: bool = True,
        skill_match_threshold: float = 0.5,
        auto_load_references: bool = True,
        auto_execute_scripts: bool = False,  # Safety: require explicit opt-in
        on_skill_selected: Callable[[Skill], None] | None = None,
        on_reference_loaded: Callable[[str, str], None] | None = None,
        on_script_executed: Callable[[str, str], None] | None = None,
    ):
        """
        Initialize the SkillAgent.

        Args:
            skill_paths: List of directories to scan for infographic-skills
            llm_client: LLM client for chat completions
            base_system_prompt: Base system prompt to use
            auto_select_skill: Automatically select matching skill
            skill_match_threshold: Minimum score for skill matching
            auto_load_references: Automatically load matching references
            auto_execute_scripts: Automatically execute scripts (use with caution)
            on_skill_selected: Callback when a skill is selected
            on_reference_loaded: Callback when a reference is loaded
            on_script_executed: Callback when a script is executed
        """
        self.skill_paths = [Path(p).expanduser() for p in skill_paths]
        self.llm_client = llm_client
        self.base_system_prompt = base_system_prompt or ""
        self.auto_select_skill = auto_select_skill
        self.skill_match_threshold = skill_match_threshold
        self.auto_load_references = auto_load_references
        self.auto_execute_scripts = auto_execute_scripts

        # Callbacks
        self.on_skill_selected = on_skill_selected
        self.on_reference_loaded = on_reference_loaded
        self.on_script_executed = on_script_executed

        # Internal state
        self._manager = SkillManager(self.skill_paths)
        self._prompt_builder = PromptBuilder()
        self._context = ConversationContext()
        self._initialized = False

    async def initialize(self) -> int:
        """
        Initialize the agent by discovering all infographic-skills.

        Returns:
            Number of infographic-skills discovered
        """
        metadata_list = await self._manager.discover()
        self._initialized = True
        return len(metadata_list)

    def reset(self):
        """Reset conversation context."""
        self._context = ConversationContext()

    @property
    def active_skill(self) -> Skill | None:
        """Get the currently active skill."""
        return self._context.active_skill

    @property
    def available_skills(self) -> list[str]:
        """Get list of available skill names."""
        return [m["name"] for m in self._manager.get_all_metadata()]

    async def select_skill(self, skill_name: str) -> bool:
        """
        Manually select a skill.

        Args:
            skill_name: Name of the skill to select

        Returns:
            True if skill was found and selected
        """
        skill = self._manager.get_skill(skill_name)
        if not skill:
            return False

        # Load full instruction
        await self._manager.load_instruction(skill_name)
        skill = self._manager.get_skill(skill_name)

        self._context.active_skill = skill
        self._context.state = AgentState.SKILL_ACTIVE

        if self.on_skill_selected:
            self.on_skill_selected(skill)

        return True

    def deselect_skill(self):
        """Deselect the current skill."""
        self._context.active_skill = None
        self._context.state = AgentState.IDLE
        self._context.loaded_references = []

    async def chat(
        self,
        content: str,
        images: list[ImageContent] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AgentResponse:
        """
        Send a chat message with automatic skill invocation.

        Args:
            content: User message content
            images: Optional images for multimodal messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional LLM parameters

        Returns:
            AgentResponse with content and metadata
        """
        if not self._initialized:
            await self.initialize()

        # Create user message
        user_message = Message.user(content, images=images or [])
        self._context.messages.append(user_message)

        # Auto-select skill if enabled and no skill is active
        skill_used = None
        if self.auto_select_skill and not self._context.active_skill:
            matched = self._manager.match(content, limit=1)
            if matched:
                # Keyword match found
                await self.select_skill(matched[0].name)
                skill_used = matched[0].name
            else:
                # No keyword match, use LLM to select
                llm_selected = await self._llm_select_skill(content)
                if llm_selected:
                    await self.select_skill(llm_selected)
                    skill_used = llm_selected

        # Load applicable references FIRST (so they're included in the prompt)
        references_loaded = []
        if self.auto_load_references and self._context.active_skill:
            references_loaded = await self._load_applicable_references(content)

        # Build system prompt (now includes loaded references)
        system_prompt = self._build_system_prompt(content)

        # Call LLM
        response = await self.llm_client.chat(
            messages=self._context.messages,
            system=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Add assistant response to context
        assistant_message = Message.assistant(response.content)
        self._context.messages.append(assistant_message)

        # Check for script invocations
        scripts_executed = []
        if self.auto_execute_scripts and self._context.active_skill:
            scripts_executed = await self._handle_script_invocations(response.content)

        return AgentResponse(
            content=response.content,
            skill_used=skill_used or (self._context.active_skill.name if self._context.active_skill else None),
            references_loaded=references_loaded,
            scripts_executed=scripts_executed,
            usage=response.usage,
        )

    async def chat_stream(
        self,
        content: str,
        images: list[ImageContent] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Send a streaming chat message with automatic skill invocation.

        Args:
            content: User message content
            images: Optional images for multimodal messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional LLM parameters

        Yields:
            Content chunks as they arrive
        """
        if not self._initialized:
            await self.initialize()

        # Create user message
        user_message = Message.user(content, images=images or [])
        self._context.messages.append(user_message)

        # Auto-select skill if enabled
        if self.auto_select_skill and not self._context.active_skill:
            matched = self._manager.match(content, limit=1)
            if matched:
                await self.select_skill(matched[0].name)
            else:
                # No keyword match, use LLM to select
                llm_selected = await self._llm_select_skill(content)
                if llm_selected:
                    await self.select_skill(llm_selected)

        # Load applicable references FIRST (so they're included in the prompt)
        if self.auto_load_references and self._context.active_skill:
            await self._load_applicable_references(content)

        # Build system prompt (now includes loaded references)
        system_prompt = self._build_system_prompt(content)

        # Stream response
        full_response = ""
        async for chunk in self.llm_client.chat_stream(
            messages=self._context.messages,
            system=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        ):
            full_response += chunk.content
            yield chunk.content

        # Add assistant response to context
        assistant_message = Message.assistant(full_response)
        self._context.messages.append(assistant_message)

    def _build_system_prompt(self, current_input: str) -> str:
        """Build the system prompt based on current state."""
        parts = []

        # Add base system prompt
        if self.base_system_prompt:
            parts.append(self.base_system_prompt)

        # Add skill content
        if self._context.active_skill:
            skill_prompt = self._prompt_builder.build_active_skill_prompt(
                self._context.active_skill,
                include_scripts=True,
                include_references=True,
            )
            parts.append(skill_prompt)
        else:
            # Show skill catalog for auto-selection hint
            all_metadata = self._manager.get_all_metadata()
            if all_metadata:
                # Only show metadata, not full catalog to save tokens
                skill_hints = []
                for m in all_metadata[:5]:  # Limit to top 5
                    skill_hints.append(f"- {m['name']}: {m['description']}")
                if skill_hints:
                    parts.append(
                        "Available capabilities:\n" + "\n".join(skill_hints)
                    )

        return "\n\n".join(parts)

    async def _load_applicable_references(self, context: str) -> list[str]:
        """Load references that match the current context using LLM evaluation."""
        if not self._context.active_skill:
            return []

        loaded = []
        skill = self._context.active_skill

        # Step 1: Immediately load "always" mode references
        always_refs = []
        refs_for_llm = []

        for ref in skill.references:
            if ref.path in self._context.loaded_references:
                continue

            if ref.mode == ReferenceMode.ALWAYS:
                always_refs.append(ref)
            else:
                # Both explicit and implicit go to LLM for evaluation
                refs_for_llm.append(ref)

        # Load "always" refs directly
        for ref in always_refs:
            try:
                content = await self._manager.load_reference(skill.name, ref.path)
                if content:
                    ref.content = content
                    self._context.loaded_references.append(ref.path)
                    loaded.append(ref.path)
                    if self.on_reference_loaded:
                        self.on_reference_loaded(ref.path, content)
            except Exception:
                pass

        # Step 2: Let LLM decide which explicit/implicit refs to load
        if refs_for_llm:
            eval_results = await self._evaluate_reference_conditions(context, refs_for_llm)

            for ref, should_load in zip(refs_for_llm, eval_results):
                if should_load:
                    try:
                        content = await self._manager.load_reference(skill.name, ref.path)
                        if content:
                            ref.content = content
                            self._context.loaded_references.append(ref.path)
                            loaded.append(ref.path)
                            if self.on_reference_loaded:
                                self.on_reference_loaded(ref.path, content)
                    except Exception:
                        pass

        return loaded

    async def _llm_select_skill(self, query: str) -> str | None:
        """
        Use LLM to intelligently select the most appropriate skill.

        Args:
            query: User input

        Returns:
            Selected skill name, or None if no match
        """
        all_metadata = self._manager.get_all_metadata()
        if not all_metadata:
            return None

        # Build skill catalog for LLM
        skills_desc = "\n".join(
            f"{i+1}. {m['name']}: {m['description']}"
            for i, m in enumerate(all_metadata)
        )

        eval_prompt = f"""Based on the user's input, select the most appropriate skill from the list below.
If none of the infographic-skills are relevant, respond with "NONE".

User input:
```
{query[:500]}
```

Available infographic-skills:
{skills_desc}

Respond with ONLY the skill name (e.g., "meeting-summary") or "NONE". No explanation needed."""

        try:
            response = await self.llm_client.chat(
                messages=[Message.user(eval_prompt)],
                system="You are a skill router. Select the most appropriate skill based on the user's intent. Respond with only the skill name or NONE.",
                temperature=0,
                max_tokens=50,
            )

            result = response.content.strip().strip('"').strip("'")

            # Check if result matches a skill name
            for m in all_metadata:
                if m["name"].lower() == result.lower():
                    return m["name"]

            return None
        except Exception:
            return None

    async def _evaluate_reference_conditions(
        self, context: str, references: list
    ) -> list[bool]:
        """Use LLM to evaluate whether references should be loaded."""
        if not references:
            return []

        # Build evaluation prompt - Claude style: LLM decides what's useful
        eval_prompt = """For each reference, decide whether it is useful for answering the user's input.

Some references have an explicit condition.
Others are general knowledge resources without conditions.

User input:
```
{context}
```

References:
{refs_list}

For each reference, respond with YES or NO only.
Respond with one line per reference in format: "1. YES" or "1. NO"
"""
        refs_list = "\n".join(
            f"{i+1}. Path: {ref.path}\n   Condition: {ref.condition or '(none, general reference)'}"
            for i, ref in enumerate(references)
        )

        try:
            response = await self.llm_client.chat(
                messages=[Message.user(eval_prompt.format(context=context[:500], refs_list=refs_list))],
                system="You are a precise assistant. Only respond with YES or NO for each reference.",
                temperature=0,
                max_tokens=100,
            )

            # Parse response
            results = []
            lines = response.content.strip().split("\n")
            for i, ref in enumerate(references):
                # Look for YES/NO in the response
                found = False
                for line in lines:
                    if line.strip().startswith(f"{i+1}.") or line.strip().startswith(f"{i+1}:"):
                        results.append("yes" in line.lower())
                        found = True
                        break
                if not found:
                    # Default to False if parsing fails (conservative)
                    results.append(False)

            return results
        except Exception:
            # On error, default to not loading (conservative)
            return [False] * len(references)

    async def _handle_script_invocations(self, response: str) -> list[str]:
        """Handle script invocations in the response."""
        if not self._context.active_skill:
            return []

        executed = []
        invocations = self._prompt_builder.extract_script_invocations(response)

        for script_name, args in invocations:
            try:
                # If no args provided, pass the response content (e.g., meeting summary)
                # Remove the [INVOKE:...] tag from the content being passed
                input_data = args if args else re.sub(r"\[INVOKE:\w+(?:\([^)]*\))?\]", "", response).strip()

                result = await self._manager.execute_script(
                    self._context.active_skill.name,
                    script_name,
                    input_data=input_data,
                )
                executed.append(script_name)

                if self.on_script_executed:
                    self.on_script_executed(script_name, result)
            except Exception:
                pass

        return executed

    async def execute_script(self, script_name: str, input_data: str = "") -> str:
        """
        Manually execute a script from the active skill.

        Args:
            script_name: Name of the script to execute
            input_data: Input data to pass to the script

        Returns:
            Script output

        Raises:
            ValueError: If no skill is active or script not found
        """
        if not self._context.active_skill:
            raise ValueError("No skill is currently active")

        return await self._manager.execute_script(
            self._context.active_skill.name,
            script_name,
            input_data=input_data,
        )

    def get_context_summary(self) -> dict:
        """Get a summary of the current conversation context."""
        return {
            "state": self._context.state.value,
            "active_skill": self._context.active_skill.name if self._context.active_skill else None,
            "message_count": len(self._context.messages),
            "loaded_references": self._context.loaded_references.copy(),
            "available_skills": self.available_skills,
        }


async def create_agent(
    skill_paths: list[str | Path],
    api_key: str | None = None,
    base_url: str | None = None,
    model: str = "gpt-4",
    **kwargs,
) -> SkillAgent:
    """
    Convenience function to create and initialize a SkillAgent.

    Args:
        skill_paths: List of skill directories
        api_key: LLM API key
        base_url: LLM base URL
        model: Model to use
        **kwargs: Additional SkillAgent options

    Returns:
        Initialized SkillAgent

    Example:
        agent = await create_agent(
            skill_paths=["~/.openskills/infographic-skills"],
            model="gpt-4-turbo",
            auto_execute_scripts=True,
        )
        response = await agent.chat("帮我总结会议")
    """
    from openskills.llm.openai_compat import OpenAICompatClient

    client = OpenAICompatClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    paths = [Path(p) for p in skill_paths]
    agent = SkillAgent(skill_paths=paths, llm_client=client, **kwargs)
    await agent.initialize()

    return agent
