.. _sphinx_ext:

Sphinx Extension
================

In addition to the CLI, ``chango`` provides a Sphinx extension that can be used to automatically render change notes in your project documentation.

Setup
-----

To enable the extension, simply add ``'chango.sphinx_ext'`` to your ``extensions`` list in your ``conf.py`` file.

.. code-block:: python

    extensions = [
        ...
        'chango.sphinx_ext',
    ]

To specify the path to the ``pyproject.toml`` file, you can use the ``chango_pyproject_toml`` configuration option in your ``conf.py`` file.

.. code-block:: python

    chango_pyproject_toml = 'path/to/pyproject.toml'

This is useful to ensure that ``chango`` can find the correct configuration file independent of the current working directory.

Now, you can use the ``chango`` directive in your documentation to render change notes.

.. code-block:: rst

    .. chango:: Headline
       :start_from: 1.0.0

This will render a list of change notes starting from version 1.0.0 up to the latest (unreleased) version.

Configuration
-------------

The following configuration options are available:

.. confval:: chango_pyproject_toml
   :type: ``pathlib.Path`` | ``str`` | ``None``
   :default: ``None``

   Path to the ``pyproject.toml`` file. Takes the same input as :func:`chango.config.get_chango_instance`.

.. rst:directive:: chango

    The ``chango`` directive renders the version history of your project.

    If the directive has a body, it will be used as the headline for the change notes with ``=``
    above and below the headline, which is the default reStructuredText syntax for a headline.

    .. admonition:: Example

        .. code-block:: rst

            .. chango:: Headline
               :start_from: "1.0.0"

        Renders as

        .. code-block:: rst

            ========
            Headline
            ========

            ...

    The options that are valid for the ``chango`` directive are the same as the options for :meth:`~chango.abc.ChanGo.load_version_history`.

    If your implementation of :class:`~chango.abc.ChanGo` has additional options, you can pass them as keyword arguments to the directive.
    ``chango`` will inspect the signature of the method and configure the options accordingly.


    .. important::

        Since the options will be interpreted as keyword arguments for :meth:`~chango.abc.ChanGo.load_version_history`, by default, each option is required to have a value.

    .. tip::

        The values be interpreted as JSON string and will be loaded using :func:`json.loads`.

    Since you can only specify strings as options in reStructuredText, it may be necessary to use custom validator functions to convert the strings to the correct types.
    Custom validators can be specified by using :class:`typing.Annotated` in the signature of the method.
    Validators should have the following signature:

    .. code-block:: python

        def validator(value: str | None) -> Any:
            ...

    .. admonition:: Example

        .. code-block:: python

            from collections.abc import Sequence
            from typing import Annotated

            def sequence_validator(value: str | None) -> Sequence[int]:
                if value is None:
                    raise ValueError('Value must not be None')
                return tuple(map(int, value.split(',')))

            def flag_validator(value: str | None) -> bool:
                if value is not None:
                    raise ValueError('Flag options must not have a value')
                return True

            class MyChanGo(ChanGo):
                def load_version_history(
                    self,
                    start_from: str | None = None,
                    end_at: str | None = None,
                    custom_option_1: dict[str, str] | None = None,
                    custom_option_2: Annotated[Sequence[int], sequence_validator] = (1, 2, 3),
                    custom_option_3: Annotated[bool, flag_validator] = False,
                ):
                    ...

        With this signature, you can use the following directive:

        .. code-block:: rst

            .. chango::
               :custom_option_1: {"key": "value"}
               :custom_option_2: 4,5,6
               :custom_option_3:

    The following options are available by default:

    Keyword Arguments:
        ``:start_from:`` (:obj:`str`, optional): The version to start from. Passed to parameter
            :paramref:`~chango.abc.ChanGo.load_version_history` of
            :meth:`~chango.abc.ChanGo.load_version_history`. Defaults to ``None``.
        ``:end_at:`` (:obj:`str`, optional): The version to end at. Passed to parameter
            :paramref:`~chango.abc.ChanGo.load_version_history` of
            :meth:`~chango.abc.ChanGo.load_version_history`. Defaults to ``None``.