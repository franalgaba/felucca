import os

import typer
import toml
from rich.console import Console
from cookiecutter.main import cookiecutter

from felucca.utils import (
    execute_poetry,
    find_dependency_version,
    get_package_name,
    install_cairo_package,
    is_felucca_package,
    set_cairo_package,
    uninstall_cairo_package,
)

app = typer.Typer()
_console = Console()


@app.command()
def install(package: str):
    if is_felucca_package(package):
        with _console.status(f"[bold green] Installing {package}..."):
            execute_poetry(f"-q add {package}")
            _console.print(
                f"[green]:heavy_check_mark: Done![/green] [bold]{package}[/bold] successfully installed :rocket:"
            )
            version = find_dependency_version(package)
            set_cairo_package(package, version)
            install_cairo_package(package)
    else:
        _console.print(
            f"Installation aborted. [bold]{package}[/bold] is not a Cairo package :sweat:"
        )


@app.command()
def uninstall(package: str):
    if is_felucca_package(package):
        with _console.status(f"[bold green] Uninstalling {package}..."):
            execute_poetry(f"-q remove {package}")
            _console.print(
                "[green]:heavy_check_mark: Done![/green] [bold]{package}[/bold] successfully uninstalled :rocket:"
            )
            version = find_dependency_version(package)
            set_cairo_package(package, version)
            uninstall_cairo_package(package)


@app.command()
def setup():

    try:
        execute_poetry("-q")
    except typer.Exit:
        _console.print(":x: Poetry is not installed. Please, first install Poetry.")
        raise typer.Exit()

    if not os.path.isfile("./pyproject.toml"):
        raise typer.Exit(
            ":x: pyproject.toml file does not exist. For setting a new package use `felucca new`."
        )

    pyproject = toml.load("./pyproject.toml")
    if pyproject["build-system"]["build-backend"] != "poetry.core.masonry.api":
        raise typer.Exit(
            ":x: Felucca is intended to be used inside a project with Poetry not Setuptools."
        )

    if "felucca" not in pyproject["tool"]["poetry"]["keywords"]:
        _console.print("Setting up package keywords...")
        if isinstance(pyproject["tool"]["poetry"]["keywords"], list):
            pyproject["tool"]["poetry"]["keywords"].append("felucca")
        else:
            pyproject["tool"]["poetry"]["keywords"] = ["felucca"]

    package_name_norm = get_package_name().replace("-", "_")
    if "include" not in pyproject["tool"]["poetry"]:
        pyproject["tool"]["poetry"]["inlcude"] = [
            f"{package_name_norm}/*.cairo",
            f"{package_name_norm}/*/*.cairo",
        ]
    else:
        pyproject["tool"]["poetry"]["inlcude"].append(f"{package_name_norm}/*.cairo")
        pyproject["tool"]["poetry"]["inlcude"].append(f"{package_name_norm}/*/*.cairo")

    with open("./pyproject.toml", "w") as file:
        toml.dump(pyproject, file)

    _console.print("[green]:heavy_check_mark: Done![/green]")


@app.command()
def new(name: str):
    cookiecutter(
        "https://github.com/franalgaba/felucca-package-template.git",
        extra_context={"project_name": name},
    )


if __name__ == "__main__":
    app()
