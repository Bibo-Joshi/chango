``chango``
==========

.. image:: https://img.shields.io/pypi/v/chango.svg
   :target: https://pypi.org/project/chango/
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/pyversions/chango.svg
   :target: https://pypi.org/project/chango/
   :alt: Supported Python versions

.. image:: https://readthedocs.org/projects/chango/badge/?version=stable
   :target: https://chango.readthedocs.io/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/l/chango.svg
   :target: https://mit-license.org/
   :alt: MIT License

.. image:: https://github.com/Bibo-Joshi/chango/actions/workflows/unit_tests.yml/badge.svg?branch=main
   :target: https://github.com/Bibo-Joshi/chango/
   :alt: Github Actions workflow

.. image:: https://codecov.io/gh/Bibo-Joshi/chango/graph/badge.svg?token=H1HUA2FDR3
   :target: https://codecov.io/gh/Bibo-Joshi/chango
   :alt: Code coverage

.. image:: https://results.pre-commit.ci/badge/github/Bibo-Joshi/chango/main.svg
   :target: https://results.pre-commit.ci/latest/github/Bibo-Joshi/chango/main
   :alt: pre-commit.ci status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

Introduction
------------

``chango`` is a changelog generation tool.
Changes are described alongside the code changes in the codebase.
``chango`` extracts these changes and generates a changelog.
``chango`` consists of both a command line interface and a Python API.
All aspects of the data formats, storage, and rendering are customizable via an interface class approach.

Installing
----------

You can install or upgrade ``chango`` via

.. code:: shell

    pipx install chango --upgrade

Note that installation via `pipx <https://pipx.pypa.io/stable/>`_ is recommended since ``chango`` should not interfere with your projects dependencies.

Motivation
----------

Informative and helpful changelogs (or release notes) are an essential part of software development.
They are a core part of the communication between developers and users.
At the same time, creating and maintaining changelogs can be a tedious and error-prone task, especially since this is often done only when a new release is prepared.
``chango`` aims to make the process of maintaining changelogs as easy as possible.
This is achieved roughly by two means:

1. **Shifting the creation of changelogs to the time of development**:
   Changes are described alongside the code changes in the codebase.
   This reduces the chance to forget about crucial details in the changes that should be mentioned in the changelog.
   It also ensures that the changelog undergoes the same review process as the code changes.
2. **Automating the generation of changelogs**:
   ``chango`` extracts the changes from the codebase and generates a changelog.
   At release time, the changelog is thus already up-to-date and requires close to zero manual work.

Inspiration
~~~~~~~~~~~

This package is heavily inspired by the `towncrier <https://towncrier.readthedocs.io/>`_  and `reno <https://reno.readthedocs.io/>`_ packages.
Both packages are excellent tools for changelog generation but are rather specialized in their use cases.
``chango`` aims to be more flexible and customizable than these packages.

Quick Start
-----------

A minimal setup of using ``chango`` for your project consists of the following steps.

Building a ``ChanGo`` instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``chango`` is designed to be highly customizable.

Store the following code in a file named ``chango.py`` in the root of your project.

.. code:: python

    from chango.concrete import (
        CommentChangeNote,
        CommentVersionNote,
        DirectoryChanGo,
        DirectoryVersionScanner,
        HeaderVersionHistory,
    )

    chango_instance = DirectoryChanGo(
        change_note_type=CommentChangeNote,
        version_note_type=CommentVersionNote,
        version_history_type=HeaderVersionHistory,
        scanner=DirectoryVersionScanner(
            base_directory="changes", unreleased_directory="unreleased"
        ),
    )

Create the directories ``changes`` and ``changes/unreleased`` in the root of your project.

The ``chango_instance`` is the object that the CLI will use to interact with the changelog.
It contains information about the data type of individual changes, versions and the history of versions.
It also has instructions on how the individual changes are stored and how they are extracted from the codebase.
All these aspects can be customized by providing different classes to the ``DirectoryChanGo`` constructor or using a different implementation of the ``ChanGo`` interface.

Configuring ``pyproject.toml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We still need to make the ``chango`` CLI aware of the ``chango_instance``.
This is done by adding the following lines to your ``pyproject.toml`` file.

.. code:: toml

    [tool.chango]
    sys_path = "."
    chango_instance = { name= "chango_instance", module = "chango" }

This instructs the CLI to import the ``chango_instance`` from the file ``chango.py`` in the root of your project.

Adding Changes
~~~~~~~~~~~~~~~

Now the ``chango`` CLI is ready to be used.
Go ahead and add a change to the ``changes/unreleased`` directory.
It's as simple als calling

.. code:: shell

    chango new short-slug-for-the-change

For more information on how to use ``chango``, please refer to the `documentation <https://chango.readthedocs.io/>`_.
