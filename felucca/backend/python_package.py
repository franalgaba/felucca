import os
import shutil
import subprocess

from felucca.core.utils import (
    execute_setuptools,
    get_package_name,
)


def remove_installation_metadata():
    """
    Remove all the installation metadata from
    Python packages
    """
    root_dir = get_package_name()

    extension = ".dist-info"

    # Search for the folder in the root directory
    for root, dirs, files in os.walk(root_dir):
        for name in dirs:
            # Check if the current folder matches the desired name
            if name.endswith(extension):
                # Remove the folder
                shutil.rmtree(os.path.join(root, name))


def install_contracts(package: str, version: str):
    """Install contracts packaged in the Python wheel

    Args:
        package (str): package name
        version (str): version of the package

    Returns:
        list: list with the contracts location
    """

    package_name = get_package_name()
    command = f"install {package}"
    if version is not None:
        command += f"=={version}"
    command += f" --no-deps --target {package_name} --quiet"

    before = os.listdir(package_name)
    execute_setuptools(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    remove_installation_metadata()
    after = os.listdir(package_name)

    return set(after).difference(before)
