import site
import os
import shutil
from pathlib import Path

import requests
import toml


def is_felucca_package(package: str):

    url = "https://pypi.org/pypi"
    response = requests.get(f"{url}/{package}/json").json()

    keywords = response["info"]["keywords"]
    return True if "felucca" in keywords else False


def find_dependency_version(package: str) -> str:

    lock = toml.load("./poetry.lock")
    for package_details in lock["package"]:
        if package in package_details["name"]:
            return package_details["version"]


def set_cairo_package(package: str, version: str):

    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    if "felucca" not in settings:
        settings["felucca"] = {}
        settings["felucca"]["contracts"] = {}
    settings["felucca"]["contracts"][f"{package}"] = version
    with open(pyproject_file, "w") as file:
        toml.dump(settings, file)


def remove_cairo_package(package):
    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    del settings["felucca"]["contracts"][f"{package}"]
    with open(pyproject_file, "w") as file:
        toml.dump(settings, file)


def get_package_name() -> str:
    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    return settings["tool"]["poetry"]["name"]


def install_cairo_package(package):
    site_packages = site.getsitepackages()[0]
    norm_package = package.replace("-", "_")
    source_package = get_package_name().replace("-", "_")
    package_contracts = os.path.join(site_packages, norm_package)
    target_dir = f"./{source_package}/{norm_package}"
    shutil.copytree(package_contracts, target_dir)

    for contract in Path(target_dir).glob("**/*.cairo"):
        content = contract.read_text()
        content = content.replace(
            f"from {norm_package}.", f"from {source_package}.{norm_package}."
        )
        contract.write_text(content)


def uninstall_cairo_package(package):

    norm_package = package.replace("-", "_")
    target_dir = f"./{get_package_name()}/{norm_package}"
    shutil.rmtree(target_dir)
