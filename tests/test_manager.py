"""Tests for the SkillManager."""

import pytest
from pathlib import Path

from openskills.core.manager import SkillManager


class TestSkillManager:
    """Tests for SkillManager."""

    @pytest.fixture
    def skill_dir(self, tmp_path):
        """Create a temporary skill directory."""
        skills_path = tmp_path / "skills"
        skills_path.mkdir()

        # Create test skill 1
        skill1_dir = skills_path / "meeting-summary"
        skill1_dir.mkdir()
        (skill1_dir / "SKILL.md").write_text("""---
name: meeting-summary
description: Summarize meetings
triggers:
  - summarize meeting
  - 会议总结
---

# Meeting Summary Instructions
""")

        # Create test skill 2
        skill2_dir = skills_path / "code-review"
        skill2_dir.mkdir()
        (skill2_dir / "SKILL.md").write_text("""---
name: code-review
description: Review code changes
triggers:
  - review code
  - code review
---

# Code Review Instructions
""")

        return skills_path

    @pytest.mark.asyncio
    async def test_discover_skills(self, skill_dir):
        manager = SkillManager([skill_dir])
        metadata_list = await manager.discover()

        assert len(metadata_list) == 2
        names = [m.name for m in metadata_list]
        assert "meeting-summary" in names
        assert "code-review" in names

    @pytest.mark.asyncio
    async def test_get_skill(self, skill_dir):
        manager = SkillManager([skill_dir])
        await manager.discover()

        skill = manager.get_skill("meeting-summary")
        assert skill is not None
        assert skill.name == "meeting-summary"

        # Instruction not loaded yet (metadata only)
        assert skill.instruction is None

    @pytest.mark.asyncio
    async def test_load_instruction(self, skill_dir):
        manager = SkillManager([skill_dir])
        await manager.discover()

        instruction = await manager.load_instruction("meeting-summary")

        assert instruction is not None
        assert "Meeting Summary" in instruction.content

    @pytest.mark.asyncio
    async def test_match_skills(self, skill_dir):
        manager = SkillManager([skill_dir])
        await manager.discover()

        # Match by exact trigger
        matched = manager.match("会议总结")
        assert len(matched) >= 1
        assert matched[0].name == "meeting-summary"

        # Match by trigger substring
        matched = manager.match("请帮我做一个会议总结")
        assert len(matched) >= 1
        assert matched[0].name == "meeting-summary"

        # Match by name/description
        matched = manager.match("code review")
        assert len(matched) >= 1
        assert matched[0].name == "code-review"

    @pytest.mark.asyncio
    async def test_discover_empty_directory(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        manager = SkillManager([empty_dir])
        metadata_list = await manager.discover()

        assert len(metadata_list) == 0

    @pytest.mark.asyncio
    async def test_discover_nonexistent_directory(self, tmp_path):
        nonexistent = tmp_path / "nonexistent"

        manager = SkillManager([nonexistent])
        metadata_list = await manager.discover()

        assert len(metadata_list) == 0

    @pytest.mark.asyncio
    async def test_get_all_metadata(self, skill_dir):
        manager = SkillManager([skill_dir])
        await manager.discover()

        all_metadata = manager.get_all_metadata()

        assert len(all_metadata) == 2
        assert all("name" in m for m in all_metadata)
        assert all("description" in m for m in all_metadata)


class TestSkillManagerWithReferences:
    """Tests for reference loading."""

    @pytest.fixture
    def skill_with_ref(self, tmp_path):
        """Create a skill with references using standard directory structure."""
        skills_path = tmp_path / "skills"
        skill_dir = skills_path / "test-skill"
        references_dir = skill_dir / "references"
        references_dir.mkdir(parents=True)

        (skill_dir / "SKILL.md").write_text("""---
name: test-skill
description: Test skill with references
references:
  - path: references/reference.md
    condition: When context mentions test
---

Instructions.
""")

        (references_dir / "reference.md").write_text("""
# Reference Document

This is reference content.
""")

        return skills_path

    @pytest.mark.asyncio
    async def test_load_reference(self, skill_with_ref):
        manager = SkillManager([skill_with_ref])
        await manager.discover()

        content = await manager.load_reference("test-skill", "references/reference.md")

        assert content is not None
        assert "Reference Document" in content
