import os
import shutil
import tempfile

import git

from felucca.core.utils import (
    get_package_name,
)


def install_protostar_contracts(package: str, version):
    """Install contracts from Protostar repository

    Args:
        package (str): package name
        version (str): version of the package

    Returns:
        list: list with the contracts location
    """

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
