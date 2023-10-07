"""ppm: python project manager.

commands
========
ppm new
ppm rm
ppm ls
ppm open
=========
"""

import os
import sys
import json
import subprocess
import shutil
import webbrowser
from pathlib import Path
from rich.console import Console
import typer
from typing import Dict
import questionary
from questionary import Style


app = typer.Typer()


def get_config() -> Path:
    """Get the config file."""
    config_file = Path.home() / ".ppm.json"
    if not config_file.exists():
        config_file.touch()
        config_file.write_text("{}")
    return config_file


def get_config_data() -> Dict[str, str]:
    """Get the config data."""
    config_file = get_config()
    config_data = json.loads(config_file.read_text())
    return config_data


def write_config_data(config_data: Dict[str, str]) -> None:
    """Write the config data."""
    config_file = get_config()
    config_file.write_text(json.dumps(config_data))


@app.command()
def new() -> None:
    """Add a project."""
    config_data = get_config_data()
    console = Console()
    project_name = questionary.text("Enter project name:").ask()
    project_path = questionary.text("Enter project path:").ask()
    project_dir = os.path.join(project_path, project_name)
    os.makedirs(project_dir, exist_ok=True)
    config_data[project_name] = project_dir
    write_config_data(config_data)
    console.print(f"[bold green]Added {project_name}.[/bold green]")

    init_git = questionary.confirm("Initialize Git repository?").ask()
    if init_git:
        os.chdir(project_dir)
        subprocess.run(["git", "init"])
        console.print(
            f"[bold green]Initialized Git repository in {project_dir}.[/bold green]"
        )

    init_poetry = questionary.confirm("Initialize Poetry for the project?").ask()
    if init_poetry:
        os.chdir(project_dir)
        subprocess.run(["poetry", "init"])
        console.print(
            f"[bold green]Initialized Poetry for the project in {project_dir}.[/bold green]"
        )


@app.command()
def rm(project_name: str) -> None:
    """Remove a project."""
    config_data = get_config_data()
    project_path = config_data.get(project_name)
    if not project_path:
        console = Console()
        console.print(f"[bold red]Project {project_name} not found.[/bold red]")
        return
    console = Console()
    confirm = questionary.confirm(
        f"Are you sure you want to remove {project_name}?"
    ).ask()
    confirm = questionary.confirm(
        f"WARNING: This permanently removes {project_name}!! Continue?",
        style=Style([("question", "bold red")]),
    ).ask()
    if confirm:
        config_data.pop(project_name)
        write_config_data(config_data)
        shutil.rmtree(project_path)
        console.print(f"[bold red]Removed {project_name}.[/bold red]")
    else:
        console.print(f"[bold green]Cancelled removal of {project_name}.[/bold green]")


@app.command()
def ls() -> None:
    """List all projects."""
    config_data = get_config_data()
    console = Console()
    for project_name, project_path in config_data.items():
        console.print(f"[bold blue]{project_name}[/bold blue]: {project_path}")


@app.command()
def open(project_name: str) -> None:
    """Open a project."""
    config_data = get_config_data()
    project_path = config_data[project_name]
    editors = ["code", "subl", "vim", "nano"]
    console = Console()
    editor = questionary.select(
        "Choose an editor to open the project in:", choices=editors
    ).ask()
    subprocess.run([editor, project_path])


if __name__ == "__main__":
    app()
