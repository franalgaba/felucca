from struct import pack
import subprocess

import typer
from rich.console import Console

from felucca.utils import (
    find_dependency_version,
    install_cairo_package,
    is_felucca_package,
    set_cairo_package,
    uninstall_cairo_package,
)

app = typer.Typer()
_console = Console()


@app.command()
def install(package: str):
    if is_felucca_package(package):
        with _console.status(f"[bold green] Installing {package}..."):
            result = subprocess.run(["poetry", "add", package, "--quiet"])
        if result.returncode == 0:
            _console.print(
                f"Done! [bold]{package}[/bold] successfully installed. Find installed Cairo contracts in the `contracts` folder :rocket:"
            )
            version = find_dependency_version(package)
            set_cairo_package(package, version)
            install_cairo_package(package)
    else:
        _console.print(
            f"Installation aborted. [bold]{package}[/bold] is not a Cairo package :sweat:"
        )


@app.command()
def uninstall(package: str):
    if is_felucca_package(package):
        with _console.status(f"[bold green] Uninstalling {package}..."):
            result = subprocess.run(["poetry", "remove", package, "--quiet"])
        if result.returncode == 0:
            _console.print(
                "Done! {package} successfully uninstalled. Cairo contracts removed from `contracts` folder :rocket:"
            )
            version = find_dependency_version(package)
            set_cairo_package(package, version)
            uninstall_cairo_package(package)


if __name__ == "__main__":
    app()
