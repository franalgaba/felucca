import os

import typer
import toml
from rich.console import Console
from cookiecutter.main import cookiecutter
from felucca.backend.poetry import (
    uninstall_cairo_package,
)
from felucca.backend.python_package import install_contracts

from felucca.core.enums import Backends
from felucca.core.utils import (
    clean_cairo_package,
    execute_poetry,
    get_package_name,
    is_felucca_package,
    is_protostar_package,
    set_cairo_package,
    find_dependency_version,
)

app = typer.Typer(help="Felucca - Package Management for Cairo")
_console = Console()


@app.command()
def install(
    package: str = typer.Argument(..., help="Name of the Cairo package from pypi"),
    version: str = typer.Argument(None, help="Version of the Cairo package to install"),
):
    """
    Install a Cairo package

    Raises:
        Exit: if there is an exception during installation.
        TypeError: requested package is not of supported types

    Args:
        package (str): Name of the Cairo package to uninstall from project
        version (str): Version of the Cairo package to install
    """

    if not is_felucca_package(package):
        _console.print(
            f"Package {package} is not a felucca package. Use `setup` for full compatibility and package awareness"
        )

    try:

        if is_protostar_package(package):
            _console.print("Soon!")
            contract_type = Backends.protostar
        else:
            try:
                contracts_location = install_contracts(package, version)
                contract_type = Backends.python
            except Exception:
                raise TypeError(
                    "Requested package is not compatible. Available compatibility: python, protostar"
                )

            command = f"add {package}"
            if version is not None:
                command += f"=={version}"
            execute_poetry(command)

            if version is None:
                version = find_dependency_version(package)
            set_cairo_package(package, version, contract_type, contracts_location)

    except typer.Exit:
        raise typer.Exit()

    _console.print(
        f"[green]:heavy_check_mark: Done![/green] [bold]{package}[/bold] successfully installed :rocket:"
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

    if not is_felucca_package(package):
        _console.print(
            f"Package {package} is not a felucca package. Use `setup` for full compatibility and package awareness"
        )

    try:
        execute_poetry(f"remove {package}")
    except typer.Exit:
        raise typer.Exit()

    clean_cairo_package(package)

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
        checkout="v0.10.3",
    )


if __name__ == "__main__":
    app()
