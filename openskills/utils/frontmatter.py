"""
YAML frontmatter parser for SKILL.md files.

Handles parsing of markdown files with YAML frontmatter sections.
"""

import re
from typing import Any

import yaml


FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n(.*)$",
    re.DOTALL
)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content.

    Args:
        content: The full markdown content including frontmatter

    Returns:
        A tuple of (frontmatter_dict, body_content)

    Raises:
        ValueError: If the frontmatter is invalid

    Example:
        >>> content = '''---
        ... name: test-skill
        ... description: A test skill
        ... ---
        ... # Instructions
        ... This is the body.
        ... '''
        >>> metadata, body = parse_frontmatter(content)
        >>> metadata['name']
        'test-skill'
        >>> 'Instructions' in body
        True
    """
    content = content.strip()

    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        # No frontmatter found
        return {}, content

    frontmatter_str = match.group(1)
    body = match.group(2)

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
        if frontmatter is None:
            frontmatter = {}
        if not isinstance(frontmatter, dict):
            raise ValueError("Frontmatter must be a YAML dictionary")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}") from e

    return frontmatter, body.strip()


def create_frontmatter(metadata: dict[str, Any], body: str) -> str:
    """
    Create markdown content with YAML frontmatter.

    Args:
        metadata: Dictionary of frontmatter data
        body: The markdown body content

    Returns:
        Complete markdown content with frontmatter
    """
    frontmatter_str = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
    return f"---\n{frontmatter_str}---\n\n{body}"
