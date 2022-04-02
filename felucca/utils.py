import requests

from benedict import benedict


def is_felucca_package(package: str):

    url = "https://pypi.org/pypi"
    response = requests.get(f"{url}/{package}/json").json()

    keywords = response["info"]["keywords"]
    return True if "felucca" in keywords else False


def find_dependency_version(package: str):

    lock = benedict("./poetry.lock")
    return lock[f"package.{package}.version"]


def set_cairo_package(package: str, version: str):
    settings = benedict("./pyproject.toml")
    settings[f"felucca.contracts.{package}"] = version
    settings.to_toml()


def remove_cairo_package(package):
    settings = benedict("./pyproject.toml")
    settings.remove(f"felucca.contracts.{package}")
    settings.to_toml()
