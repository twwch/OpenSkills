"""
OpenSkills CLI - Command line interface for managing and using infographic-skills.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

from openskills.core.manager import SkillManager
from openskills.core.parser import SkillParser

app = typer.Typer(
    name="openskills",
    help="OpenSkills - An open-source Agent Skill framework",
    add_completion=False,
)

console = Console()

# Default skill paths
DEFAULT_SKILL_PATHS = [
    Path("~/.openskills/infographic-skills"),
    Path("./.infographic-skills"),
]


def get_manager(skill_paths: list[Path] | None = None) -> SkillManager:
    """Create a SkillManager with default paths."""
    paths = skill_paths or DEFAULT_SKILL_PATHS
    return SkillManager([p.expanduser() for p in paths])


@app.command()
def list(
    path: Optional[Path] = typer.Option(
        None,
        "--path", "-p",
        help="Additional path to scan for infographic-skills",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed information",
    ),
):
    """List all available infographic-skills."""
    paths = DEFAULT_SKILL_PATHS.copy()
    if path:
        paths.append(path)

    manager = get_manager(paths)

    async def _list():
        metadata_list = await manager.discover()

        if not metadata_list:
            console.print("[yellow]No infographic-skills found.[/yellow]")
            console.print(f"Searched in: {', '.join(str(p) for p in paths)}")
            return

        table = Table(title="Available Skills")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Version", style="blue")

        if verbose:
            table.add_column("Triggers", style="magenta")
            table.add_column("Source", style="dim")

        for meta in metadata_list:
            row = [meta.name, meta.description, meta.version]
            if verbose:
                triggers = ", ".join(meta.triggers) if meta.triggers else "-"
                skill = manager.get_skill(meta.name)
                source = str(skill.source_path) if skill and skill.source_path else "-"
                row.extend([triggers, source])
            table.add_row(*row)

        console.print(table)

    asyncio.run(_list())


@app.command()
def show(
    name: str = typer.Argument(..., help="Skill name to show"),
    path: Optional[Path] = typer.Option(
        None,
        "--path", "-p",
        help="Additional path to scan for infographic-skills",
    ),
):
    """Show detailed information about a skill."""
    paths = DEFAULT_SKILL_PATHS.copy()
    if path:
        paths.append(path)

    manager = get_manager(paths)

    async def _show():
        await manager.discover()
        skill = manager.get_skill(name)

        if not skill:
            console.print(f"[red]Skill not found: {name}[/red]")
            raise typer.Exit(1)

        # Load full content
        await manager.load_instruction(name)

        # Display metadata
        console.print(Panel(
            f"[bold cyan]{skill.name}[/bold cyan] v{skill.metadata.version}\n\n"
            f"{skill.description}",
            title="Skill Info",
        ))

        # Display triggers
        if skill.metadata.triggers:
            console.print("\n[bold]Triggers:[/bold]")
            for trigger in skill.metadata.triggers:
                console.print(f"  - {trigger}")

        # Display references
        if skill.references:
            console.print("\n[bold]References:[/bold]")
            for ref in skill.references:
                condition = f" (when: {ref.condition})" if ref.condition else ""
                console.print(f"  - {ref.path}{condition}")

        # Display scripts
        if skill.scripts:
            console.print("\n[bold]Scripts:[/bold]")
            for script in skill.scripts:
                console.print(f"  - {script.name}: {script.description}")

        # Display instruction
        if skill.instruction:
            console.print("\n[bold]Instructions:[/bold]")
            console.print(Panel(
                Markdown(skill.instruction.content),
                border_style="dim",
            ))

    asyncio.run(_show())


@app.command()
def validate(
    path: Path = typer.Argument(..., help="Path to SKILL.md file or directory"),
):
    """Validate a skill file."""
    path = path.expanduser().resolve()

    if path.is_dir():
        skill_file = path / "SKILL.md"
    else:
        skill_file = path

    if not skill_file.exists():
        console.print(f"[red]File not found: {skill_file}[/red]")
        raise typer.Exit(1)

    parser = SkillParser()

    try:
        skill = parser.parse_file(skill_file)

        console.print("[green]Skill is valid![/green]")
        console.print(f"\nName: [cyan]{skill.name}[/cyan]")
        console.print(f"Description: {skill.description}")
        console.print(f"Version: {skill.metadata.version}")

        if skill.references:
            console.print(f"References: {len(skill.references)}")
            for ref in skill.references:
                ref_path = skill.resolve_reference_path(ref)
                exists = ref_path and ref_path.exists()
                status = "[green]OK[/green]" if exists else "[red]MISSING[/red]"
                console.print(f"  - {ref.path} {status}")

        if skill.scripts:
            console.print(f"Scripts: {len(skill.scripts)}")
            for script in skill.scripts:
                script_path = skill.resolve_script_path(script)
                exists = script_path and script_path.exists()
                status = "[green]OK[/green]" if exists else "[red]MISSING[/red]"
                console.print(f"  - {script.name} ({script.path}) {status}")

    except ValueError as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def init(
    path: Path = typer.Argument(
        Path("."),
        help="Directory to create the skill in",
    ),
    name: str = typer.Option(
        ...,
        "--name", "-n",
        prompt="Skill name",
        help="Name of the skill",
    ),
    description: str = typer.Option(
        ...,
        "--description", "-d",
        prompt="Skill description",
        help="Description of the skill",
    ),
    with_example: bool = typer.Option(
        False,
        "--with-example", "-e",
        help="Include example reference and script files",
    ),
):
    """Initialize a new skill from template."""
    path = path.expanduser().resolve()

    # Create skill directory structure
    skill_dir = path / name
    references_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"

    skill_dir.mkdir(parents=True, exist_ok=True)
    references_dir.mkdir(exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)

    # Create SKILL.md
    if with_example:
        skill_content = f"""---
name: {name}
description: {description}
version: 1.0.0
triggers:
  - "{name}"
  - "{name.replace('-', ' ')}"
references:
  - path: references/handbook.md
    condition: "当需要参考手册时加载"
    description: 参考手册
scripts:
  - name: process
    path: scripts/process.py
    description: 处理并输出结果
    args:
      - input
    timeout: 30
---

# {name.replace("-", " ").title()}

## Overview

{description}

## Instructions

[Add your instructions here]

## Examples

[Add examples here]
"""
        # Create example reference
        handbook_content = f"""# {name.replace("-", " ").title()} Handbook

## Guidelines

[Add your guidelines here]

## Reference

[Add reference content here]
"""
        (references_dir / "handbook.md").write_text(handbook_content)

        # Create example script
        script_content = '''#!/usr/bin/env python3
"""
Example script for processing.
"""

import json
import sys


def main():
    """Main entry point."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.stdin.seek(0)
        input_data = {"input": sys.stdin.read()}

    result = {
        "status": "success",
        "message": "Processing completed",
        "data": input_data,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
'''
        (scripts_dir / "process.py").write_text(script_content)
    else:
        skill_content = f"""---
name: {name}
description: {description}
version: 1.0.0
triggers:
  - "{name}"
  - "{name.replace('-', ' ')}"
references: []
scripts: []
---

# {name.replace("-", " ").title()}

## Overview

{description}

## Instructions

[Add your instructions here]

## Examples

[Add examples here]
"""

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill_content)

    console.print(f"[green]Skill created at: {skill_dir}[/green]")
    console.print(f"\n[bold]Directory structure:[/bold]")
    console.print(f"  {skill_dir.name}/")
    console.print(f"  ├── SKILL.md")
    console.print(f"  ├── references/    # Put reference documents here")
    console.print(f"  └── scripts/       # Put executable scripts here")
    if with_example:
        console.print(f"\n[dim]Example files created in references/ and scripts/[/dim]")


@app.command()
def match(
    query: str = typer.Argument(..., help="Query to match against infographic-skills"),
    path: Optional[Path] = typer.Option(
        None,
        "--path", "-p",
        help="Additional path to scan for infographic-skills",
    ),
    limit: int = typer.Option(
        5,
        "--limit", "-l",
        help="Maximum number of results",
    ),
):
    """Find infographic-skills matching a query."""
    paths = DEFAULT_SKILL_PATHS.copy()
    if path:
        paths.append(path)

    manager = get_manager(paths)

    async def _match():
        await manager.discover()
        matched = manager.match(query)[:limit]

        if not matched:
            console.print(f"[yellow]No infographic-skills match: {query}[/yellow]")
            return

        console.print(f"[bold]Skills matching: [cyan]{query}[/cyan][/bold]\n")

        for i, skill in enumerate(matched, 1):
            console.print(f"{i}. [cyan]{skill.name}[/cyan]: {skill.description}")

    asyncio.run(_match())


@app.command()
def run(
    name: str = typer.Argument(..., help="Skill name to run"),
    script: str = typer.Argument(..., help="Script name to execute"),
    path: Optional[Path] = typer.Option(
        None,
        "--path", "-p",
        help="Additional path to scan for infographic-skills",
    ),
):
    """Run a skill script."""
    paths = DEFAULT_SKILL_PATHS.copy()
    if path:
        paths.append(path)

    manager = get_manager(paths)

    async def _run():
        await manager.discover()

        try:
            result = await manager.execute_script(name, script)
            console.print(Panel(result, title=f"Script Output: {script}"))
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(_run())


@app.callback()
def main():
    """
    OpenSkills - An open-source Agent Skill framework.

    Implements the progressive disclosure architecture for AI agent infographic-skills.
    """
    pass


if __name__ == "__main__":
    app()
