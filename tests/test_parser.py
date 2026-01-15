"""Tests for the SKILL.md parser."""

import pytest
from pathlib import Path

from openskills.core.parser import SkillParser
from openskills.utils.frontmatter import parse_frontmatter


class TestFrontmatterParser:
    """Tests for frontmatter parsing."""

    def test_parse_valid_frontmatter(self):
        content = """---
name: test-skill
description: A test skill
version: 1.0.0
---

# Instructions

This is the body.
"""
        metadata, body = parse_frontmatter(content)

        assert metadata["name"] == "test-skill"
        assert metadata["description"] == "A test skill"
        assert metadata["version"] == "1.0.0"
        assert "Instructions" in body

    def test_parse_no_frontmatter(self):
        content = "# Just markdown\n\nNo frontmatter here."
        metadata, body = parse_frontmatter(content)

        assert metadata == {}
        assert "Just markdown" in body

    def test_parse_empty_frontmatter(self):
        content = """---
---

Body content.
"""
        metadata, body = parse_frontmatter(content)

        assert metadata == {}
        assert "Body content" in body

    def test_parse_with_triggers(self):
        content = """---
name: meeting-summary
description: Summarize meetings
triggers:
  - "summarize meeting"
  - "会议总结"
---

# Meeting Summary
"""
        metadata, body = parse_frontmatter(content)

        assert metadata["name"] == "meeting-summary"
        assert len(metadata["triggers"]) == 2
        assert "summarize meeting" in metadata["triggers"]


class TestSkillParser:
    """Tests for the skill parser."""

    def test_parse_minimal_skill(self):
        content = """---
name: minimal
description: A minimal skill
---

Instructions here.
"""
        parser = SkillParser()
        skill = parser.parse_content(content)

        assert skill.name == "minimal"
        assert skill.description == "A minimal skill"
        assert skill.metadata.version == "1.0.0"  # default
        assert skill.instruction is not None
        assert "Instructions here" in skill.instruction.content

    def test_parse_metadata_only(self):
        content = """---
name: test
description: Test skill
---

Long instructions...
"""
        parser = SkillParser()
        skill = parser.parse_content(content, metadata_only=True)

        assert skill.name == "test"
        assert skill.instruction is None  # Not loaded

    def test_parse_with_references(self):
        content = """---
name: test
description: Test
references:
  - path: references/doc.md
    condition: When needed
---

Body.
"""
        parser = SkillParser()
        skill = parser.parse_content(content)

        assert len(skill.references) == 1
        assert skill.references[0].path == "references/doc.md"
        assert skill.references[0].condition == "When needed"

    def test_parse_with_scripts(self):
        content = """---
name: test
description: Test
scripts:
  - name: upload
    path: scripts/upload.py
    description: Upload files
---

Body.
"""
        parser = SkillParser()
        skill = parser.parse_content(content)

        assert len(skill.scripts) == 1
        assert skill.scripts[0].name == "upload"
        assert skill.scripts[0].path == "scripts/upload.py"

    def test_parse_missing_required_fields(self):
        content = """---
name: test
---

Body.
"""
        parser = SkillParser()

        with pytest.raises(ValueError) as exc_info:
            parser.parse_content(content)

        assert "description" in str(exc_info.value)


class TestSkillFromFile:
    """Tests for parsing skills from files."""

    def test_parse_example_skill(self, tmp_path):
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: A test skill for testing
version: 2.0.0
triggers:
  - test
  - testing
---

# Test Skill

This is a test skill.
""")

        parser = SkillParser()
        skill = parser.parse_file(skill_file)

        assert skill.name == "test-skill"
        assert skill.metadata.version == "2.0.0"
        assert len(skill.metadata.triggers) == 2
        assert skill.source_path == skill_file
