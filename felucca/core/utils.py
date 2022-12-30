import os
import re
import shutil
import site
import subprocess

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


def execute_setuptools(command: str, **kwargs) -> None:
    """
    Execute a pip command with subprocess

    Raises:
        RuntimeError: if no pip installation is available

    Args:
        command (str): command to execute
    """

    if is_package_installed("pip"):
        executable = "pip"
    elif is_package_installed("pip3"):
        executable = "pip3"
    else:
        raise RuntimeError(
            "No pip installation available. Please install pip in your environment"
        )

    execute_subprocess(f"{executable} {command}", **kwargs)


def is_package_installed(package: str) -> bool:
    """Check if a specific Python package is installed

    Args:
        package (str): name of the package to check

    Returns:
        bool: if the package is present in the system
    """
    return shutil.which(package)


def is_felucca_package(package: str) -> bool:
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


def get_package_location(package: str) -> str:
    """Get the package location from the site-packages

    Args:
        package (str): package name

    Returns:
        str: path of the installed package
    """
    site_packages = site.getsitepackages()[0]
    norm_package = package.replace("-", "_")
    for package in os.walk(site_packages):
        if norm_package in package:
            contracts_package = os.path.join(site_packages, package)
            break
    return contracts_package


def is_protostar_package(package: str) -> bool:
    """Check if the package is a Protostar repo

    Args:
        package (str): repository location

    Returns:
        bool: if the package name is a protostar repo
    """
    # Match protostar Git repo specification
    pattern = r"^[\w-]+/[\w-]+(@v\d+\.\d+\.\d+)?$"
    return re.match(pattern, package)


def clean_cairo_package(package: str):
    """Clean installed Cairo packages

    Args:
        package (str): name of the package

    Raises:
        Exit: if felucca is not setup
        Exit: if the package is not installed
    """
    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)

    if "felucca" not in settings:
        raise typer.Exit("Felucca pacakges are not setup")
    if package not in settings["felucca"]["contracts"]:
        raise typer.Exit(f"Package {package} is not installed")

    locations = settings["felucca"]["contracts"][package]["location"]
    norm_package = get_package_name().replace("-", "_")
    for loc in locations:
        shutil.rmtree(os.path.join(norm_package, loc))
    del settings["felucca"]["contracts"][package]
    with open(pyproject_file, "w") as file:
        toml.dump(settings, file)


def set_cairo_package(
    package: str, version: str, contract_type: str, contracts_location: str
):
    """
    Set specific Cairo package version installed in pyproject.toml

    Args:
        package (str): package name
        version (str): package version
        contract_type (str): type of the package
        contracts_location (str): location of the contracts
    """

    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    if "felucca" not in settings:
        settings["felucca"] = {}
        settings["felucca"]["contracts"] = {}
    settings["felucca"]["contracts"][f"{package}"] = {}
    settings["felucca"]["contracts"][f"{package}"]["version"] = version
    settings["felucca"]["contracts"][f"{package}"]["type"] = contract_type
    settings["felucca"]["contracts"][f"{package}"]["location"] = contracts_location
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


def find_dependency_version(package: str) -> str:
    """
    Find dependency version from lock file

    Args:
        package (str): package to find

    Returns:
        str: version of the package
    """

    import pkg_resources

    return pkg_resources.get_distribution(package).version
