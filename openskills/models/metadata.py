"""
Skill metadata model - Layer 1 (Always loaded).

The metadata layer contains lightweight information used for skill discovery
and matching. This is always loaded to enable quick indexing.
"""

from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """
    First layer: Metadata (always loaded).

    Contains essential information for skill discovery and matching.
    This should be kept lightweight to minimize memory usage when
    many infographic-skills are registered.
    """

    name: str = Field(
        ...,
        description="Unique identifier for the skill",
        examples=["meeting-summary", "code-review"],
    )

    description: str = Field(
        ...,
        description="Brief description of what the skill does",
        examples=["Generates meeting summaries in a structured format"],
    )

    version: str = Field(
        default="1.0.0",
        description="Semantic version of the skill",
        pattern=r"^\d+\.\d+\.\d+.*$",
    )

    triggers: list[str] = Field(
        default_factory=list,
        description="Keywords or phrases that trigger this skill",
        examples=[["summarize meeting", "meeting notes", "会议总结"]],
    )

    author: str | None = Field(
        default=None,
        description="Author of the skill",
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization",
        examples=[["productivity", "meeting", "summary"]],
    )

    def matches_query(self, query: str) -> bool:
        """
        Check if this skill matches a user query.

        Args:
            query: User input to match against

        Returns:
            True if the skill matches the query
        """
        query_lower = query.lower()

        # Check triggers
        for trigger in self.triggers:
            if trigger.lower() in query_lower:
                return True

        # Check name and description
        if self.name.lower() in query_lower:
            return True

        # Check if any significant words from description match
        desc_words = self.description.lower().split()
        for word in desc_words:
            if len(word) > 3 and word in query_lower:
                return True

        return False
