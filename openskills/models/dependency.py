"""
Skill dependency models - Package and system dependencies for skills.

Dependencies define what packages and system commands need to be
installed/executed before running a skill's scripts.
"""

from typing import Any

from pydantic import BaseModel, Field


class SkillDependency(BaseModel):
    """
    Dependency configuration for a skill.

    Specifies Python packages and system commands that need to be
    installed/executed before the skill can run.

    Example SKILL.md configuration:
        ---
        name: docx-processor
        dependency:
          python:
            - PyMuPDF==1.23.8
            - python-docx==0.8.11
            - Pillow>=9.0
          system:
            - mkdir -p output/images
        ---
    """

    python: list[str] = Field(
        default_factory=list,
        description="Python packages to install (pip format)",
        examples=[["numpy>=1.20", "pandas==2.0.0", "requests"]],
    )

    system: list[str] = Field(
        default_factory=list,
        description="System commands to execute for setup",
        examples=[["mkdir -p output/images", "chmod +x scripts/*.sh"]],
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SkillDependency":
        """
        Parse dependency configuration from frontmatter dict.

        Args:
            data: Dictionary from SKILL.md frontmatter, or None

        Returns:
            SkillDependency instance
        """
        if not data:
            return cls()

        return cls(
            python=data.get("python", []),
            system=data.get("system", []),
        )

    def has_dependencies(self) -> bool:
        """Check if any dependencies are defined."""
        return bool(self.python or self.system)

    def get_pip_install_command(self) -> str | None:
        """
        Generate pip install command for Python dependencies.

        Returns:
            pip install command string, or None if no Python dependencies
        """
        if not self.python:
            return None
        packages = " ".join(f'"{pkg}"' for pkg in self.python)
        return f"pip install {packages}"

    def get_pip_packages(self) -> list[str]:
        """Get list of Python packages for installation."""
        return self.python.copy()

    def get_system_commands(self) -> list[str]:
        """Get list of system commands to execute."""
        return self.system.copy()
