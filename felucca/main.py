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

app = typer.Typer(help="Felucca - Package Management for Cairo")
_console = Console()


@app.command()
def install(
    package: str = typer.Argument(..., help="Name of the Cairo package from pypi")
):

    """
    Install a Cairo package

    Args:
        package (str): Name of the Cairo package to uninstall from project
    """
    if is_felucca_package(package):
        try:
            execute_poetry(f"add {package}")
        except typer.Exit:
            raise typer.Exit()
        version = find_dependency_version(package)
        set_cairo_package(package, version)
        install_cairo_package(package)
        _console.print(
            f"[green]:heavy_check_mark: Done![/green] [bold]{package}[/bold] successfully installed :rocket:"
        )
    else:
        _console.print(
            f"Installation aborted. [bold]{package}[/bold] is not a Cairo package :sweat:"
        )


@app.command()
def uninstall(
    package: str = typer.Argument(
        ..., help="Name of the Cairo package to uninstall from project"
    )
):
    """
    Uninstall a Cairo package

    Args:
        package (str): Name of the Cairo package to uninstall from project
    """
    if is_felucca_package(package):
        try:
            execute_poetry(f"remove {package}")
        except typer.Exit:
            raise typer.Exit()

        version = find_dependency_version(package)
        set_cairo_package(package, version)
        uninstall_cairo_package(package)
    _console.print(
        f"[green]:heavy_check_mark: Done![/green] [bold]{package}[/bold] successfully uninstalled :rocket:"
    )


@app.command()
def setup():
    """
    Make an existing Cairo package compatible with Felucca

    Raises:
        typer.Exit: if Poetry not installed
        typer.Exit: if not pyproject.toml file exists
        typer.Exit: if Poetry is not used in pyproject.toml
    """

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
def new(name: str = typer.Argument(..., help="Name of the Cairo package to create")):
    """
    Create a Cairo package project structure

    Args:
        name (str): Cairo package name to create
    """
    cookiecutter(
        "https://github.com/franalgaba/felucca-package-template.git",
        extra_context={"project_name": name},
        checkout="v0.10.3"
    )


if __name__ == "__main__":
    app()
