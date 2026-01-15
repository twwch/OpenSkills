"""Tests for the SkillMatcher."""

import pytest

from openskills.core.matcher import SkillMatcher
from openskills.models.metadata import SkillMetadata


class TestSkillMatcher:
    """Tests for SkillMatcher."""

    @pytest.fixture
    def metadata_list(self):
        """Create test metadata."""
        return [
            SkillMetadata(
                name="meeting-summary",
                description="Summarize meetings and create notes",
                triggers=["summarize meeting", "会议总结", "meeting notes"],
            ),
            SkillMetadata(
                name="code-review",
                description="Review code changes and provide feedback",
                triggers=["review code", "code review", "PR review"],
            ),
            SkillMetadata(
                name="email-draft",
                description="Draft professional emails",
                triggers=["write email", "draft email"],
                tags=["email", "communication"],
            ),
        ]

    def test_exact_trigger_match(self, metadata_list):
        matcher = SkillMatcher()
        results = matcher.match("summarize meeting", metadata_list)

        assert len(results) >= 1
        assert results[0].name == "meeting-summary"

    def test_partial_trigger_match(self, metadata_list):
        matcher = SkillMatcher()
        results = matcher.match("please summarize this meeting for me", metadata_list)

        assert len(results) >= 1
        assert results[0].name == "meeting-summary"

    def test_chinese_trigger_match(self, metadata_list):
        matcher = SkillMatcher()
        results = matcher.match("帮我做一个会议总结", metadata_list)

        assert len(results) >= 1
        assert results[0].name == "meeting-summary"

    def test_description_match(self, metadata_list):
        matcher = SkillMatcher()
        results = matcher.match("I need to create meeting notes", metadata_list)

        # Should match based on "meeting" and "notes" in description/triggers
        assert len(results) >= 1

    def test_tag_match(self, metadata_list):
        matcher = SkillMatcher()
        results = matcher.match("help with email", metadata_list)

        assert len(results) >= 1
        assert results[0].name == "email-draft"

    def test_no_match(self, metadata_list):
        matcher = SkillMatcher()
        results = matcher.match("xyz123 random nonsense", metadata_list)

        # Should have no matches or very low scores
        assert len(results) == 0

    def test_find_best_match(self, metadata_list):
        matcher = SkillMatcher()
        best = matcher.find_best_match("review code", metadata_list)

        assert best is not None
        assert best.name == "code-review"

    def test_limit_results(self, metadata_list):
        matcher = SkillMatcher()
        results = matcher.match("meeting", metadata_list, limit=1)

        assert len(results) <= 1

    def test_min_score_threshold(self, metadata_list):
        # High threshold
        matcher = SkillMatcher(min_score=0.9)
        results = matcher.match("meeting related stuff", metadata_list)

        # Should have fewer or no matches with high threshold
        # Only exact trigger matches should pass
        for result in results:
            # Verify any result has high relevance
            assert "meeting" in result.name or any("meeting" in t for t in result.triggers)
