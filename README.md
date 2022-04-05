# Felucca: Dependency Management for Cairo

[![Tests and release](https://github.com/franalgaba/felucca/actions/workflows/release.yml/badge.svg)](https://github.com/franalgaba/felucca/actions/workflows/release.yml)

Felucca helps you declare, manage and install dependencies of Cairo projects, ensuring you have the right stack everywhere.

# Installation

It supports Python 3.7+:

`pip install felucca`

# Introduction

`felucca` is a tool to handle Cairo contracts installation as well as its packaging levaraging Python native capabilities. Felucca uses [Poetry](https://github.com/python-poetry/poetry) under the hood to handle all Python project management using the [standardized](https://peps.python.org/pep-0518/) `pyproject.toml`.

# Why?

Cairo contracts development works very closely with Python for project management, dependency installation and testing. Felucca tries to simplify the process of sharing, installing and managing Cairo contracts between differents projects and working in a more natural manner where packages evolve over time and dependant projects doesn't have to upgrade Cairo contracts manually. Using Felucca's approach to leverage Python capabilties in terms of dependency management and project structure gives many advantages:

* Unified project structure across Cairo packages.
* Rapid adaptation to changes as the ecosystem evolves.
* Compatibility management between Cairo contracts with different Cairo versions.
* Effortless installation for quick usage in new packages.
* Traceability of Cairo packages and releases.
* Global availability of Cairo packages.
* Many more...

# Usage

This tool provides a set of different command to handle all the product lifecycle for dependency and package management. 

## Cairo package project structure creation

`felucca new <package_name>`

This command will create a project structure for Cairo packages from a [template](https://github.com/franalgaba/felucca-package-template) ready to be used for development.

## Cairo package installation

`felucca install felucca-package-example`

This command will install the Cairo package into the project while checking Cairo compatibility, keeping traceability using the `pyproject.toml` file to save required metadata and installing the Cairo contracts into the project.

## Cairo package uninstall

`felucca uninstall felucca-package-example`

This command will remove the Cairo package from the project and all the related metadata.

## Cairo package setup

`felucca setup`

If you want to check if your project is ready to work as a Cairo package this command will check all the needed requirements to do so. If not properly setup it will fix it for you automatically.

