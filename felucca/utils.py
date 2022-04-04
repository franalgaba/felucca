import requests

import toml


def is_felucca_package(package: str):

    url = "https://pypi.org/pypi"
    response = requests.get(f"{url}/{package}/json").json()

    keywords = response["info"]["keywords"]
    return True if "felucca" in keywords else False


def find_dependency_version(package: str) -> str:

    lock = toml.load("./poetry.lock")
    return lock["package"][f"{package}"]["version"]


def set_cairo_package(package: str, version: str):

    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    settings["felucca"]["contracts"][f"{package}"] = version
    with open(pyproject_file) as file:
        toml.dump(settings, file)


def remove_cairo_package(package):
    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    del settings["felucca"]["contracts"][f"{package}"]
    with open(pyproject_file) as file:
        toml.dump(settings, file)


def get_package_name() -> str:
    pyproject_file = "./pyproject.toml"
    settings = toml.load(pyproject_file)
    return settings["tool"]["poetry"]["name"]