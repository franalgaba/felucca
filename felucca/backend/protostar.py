import os
import shutil
import tempfile

import git
import toml

from felucca.core.utils import (
    get_package_name,
)


def remove_installation_metadata():
    root_dir = get_package_name()

    extension = ".dist-info"

    # Search for the folder in the root directory
    for root, dirs, files in os.walk(root_dir):
        for name in dirs:
            # Check if the current folder matches the desired name
            if name.endswith(extension):
                # Remove the folder
                shutil.rmtree(os.path.join(root, name))


def install_protostar_contracts(package: str, version):

    # Create a temporary directory
    temp_dir = tempfile.TemporaryDirectory()

    # Clone the repository
    git.Repo.clone_from(
        f"https://github.com/{package}.git", temp_dir.name, branch=version
    )

    contracts_location = "src"
    source_package = get_package_name().replace("-", "_")

    target_dir = f"./{source_package}/{contracts_location}"
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    before = os.listdir(target_dir)
    shutil.copytree(
        os.path.join(temp_dir.name, contracts_location), target_dir, dirs_exist_ok=True
    )
    # Don't forget to clean up the temporary directory
    temp_dir.cleanup()
    after = os.listdir(target_dir)
    added = set(after).difference(before)
    return map(lambda x: os.path.join(contracts_location, x), added)
