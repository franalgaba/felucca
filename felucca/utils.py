import site
import os
import shutil
import subprocess
from pathlib import Path

import requests
import toml
import typer


def execute_subprocess(command: str, **kwargs) -> None:
    """
    Execute a subprocess given a command

    Args:
        command (str): command to execute
        kwargs: extra args for subprocess

    Raises:
        Exit: if the command fails
    """

    try:
        subprocess.run(
            command, shell=True, universal_newlines=True, check=True, **kwargs
        )
    except subprocess.CalledProcessError:
        raise typer.Exit(code=1)


def execute_poetry(command: str) -> None:
    """
    Execute a poetry command with subprocess

    Args:
        command (str): command to execute
    """

    poetry = "$HOME/.poetry/bin/poetry"
    if "POETRY_HOME" in os.environ:
        poetry = "$POETRY_HOME/bin/poetry"
    execute_subprocess(f"{poetry} {command}")


def is_felucca_package(package: str):
    """
    Check if package from pypi is a Felucca package

    Args:
        package (str): pacakge name from pypi

    Returns:
        bool: true if compatible false otherwise
    """

    url = "https://pypi.org/pypi"
    response = requests.get(f"{url}/{package}/json").json()

    keywords = response["info"]["keywords"]
    return True if "felucca" in keywords else False


def find_dependency_version(package: str) -> str:
    """
    Find dependency version from lock file

    Args:
        package (str): package to find

    Returns:
        str: version of the package
    """

    if not os.path.isfile("./poetry.lock"):
        try:
            execute_poetry("install")
        except typer.Exit:
            raise typer.Exit()

    lock = toml.load("./poetry.lock")
    for package_details in lock["package"]:
        if package in package_details["name"]:
            return package_details["version"]


def set_cairo_package(package: str, version: str):
    """
    Set specific Cairo package version installed in pyproject.toml

    Args:
        package (str): package name
        version (str): package version
    """

    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    if "felucca" not in settings:
        settings["felucca"] = {}
        settings["felucca"]["contracts"] = {}
    settings["felucca"]["contracts"][f"{package}"] = version
    with open(pyproject_file, "w") as file:
        toml.dump(settings, file)


def remove_cairo_package(package: str):
    """
    Remove Cairo package from project

    Args:
        package (str): name of the package
    """
    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    del settings["felucca"]["contracts"][f"{package}"]
    with open(pyproject_file, "w") as file:
        toml.dump(settings, file)


def get_package_name() -> str:
    """

    Get current Cairo package name

    Returns:
        str: current Cairo package name
    """
    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    return settings["tool"]["poetry"]["name"]


def install_cairo_package(package: str):
    """
    Install Cairo contracts from package in project

    Args:
        package (str): package to install
    """

    site_packages = site.getsitepackages()[0]
    norm_package = package.replace("-", "_")
    source_package = get_package_name().replace("-", "_")
    package_contracts = os.path.join(site_packages, norm_package)
    target_dir = f"./{source_package}/{norm_package}"
    shutil.copytree(
        package_contracts,
        target_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.py"),
    )

    for contract in Path(target_dir).glob("**/*.cairo"):
        content = contract.read_text()
        content = content.replace(
            f"from {norm_package}.", f"from {source_package}.{norm_package}."
        )
        contract.write_text(content)


def uninstall_cairo_package(package):
    """
    Uninstall Cairo contracts from package in project

    Args:
        package (str): package to uninstall
    """

    norm_package = package.replace("-", "_")
    target_dir = f"./{get_package_name()}/{norm_package}"
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
