.. _action:

GitHub Actions
==============

When using ``chango`` in your project, you will want to ensure that each change adds a change note.
When hosted on `GitHub <https://github.com>`_, you can use `GitHub Actions <https://github.com/features/actions>`_ to support this process and automatically create a template change note for each new change.
``chango`` defines the following methods to help you with this process:

* :meth:`chango.abc.ChanGo.build_github_event_change_note`
* :meth:`chango.abc.ChangeNote.build_from_github_event`

Going even further, ``chango`` provides a composite `GitHub Action <https://github.com/marketplace/actions/chango>`_ that does the heavy lifting for you.
You can configure it for example as follows:

.. code:: yaml

    name: Create Chango Change Note
    on:
      pull_request:
        branches:
          - main
        types:
          - opened
          - reopened

    jobs:
      create-chango-fragment:
        permissions:
          # Give the default GITHUB_TOKEN write permission to commit and push the
          # added chango note to the PR branch.
          contents: write
        name: create-chango-fragment
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
          - uses: Bibo-Joshi/chango@<sha-of-latest-release>
            with:
              # Optional: Specify a Python version to use
              python-version: '3.13'

This will automatically use your ``chango`` configuration to create a change note for each new change.

Inputs
------

The following inputs can be used to configure the action using the ``with`` keyword.

.. list-table::
   :width: 95%
   :align: left
   :header-rows: 1

   * - Name
     - Description
     - Required
     - Default
   * - python-version
     - The Python version to use.
     - No
     - 3.x
   * - commit-and-push
     - Whether to commit and push the change note to the PR branch.
     - No
     - true
   * - pyproject-toml
     - Path to the ``pyproject.toml`` file. Takes the same input as :func:`chango.config.get_chango_instance`.
     - No
     - :obj:`None`
   * - data
     - Additional JSON data to pass to the parameter :paramref:`~chango.abc.ChanGo.build_github_event_change_note.data` of  :meth:`chango.abc.ChanGo.build_github_event_change_note`.
     - No
     - An instance of :class:`chango.action.ChanGoActionData`
   * - github-token:
     - GitHub Token or Personal Access Token (PAT) used to authenticate with GitHub.
     - No
     - ``GITHUB_TOKEN``
   * - query-issue-types:
     - Whether to query the issue types of the linked issues. Can only be used on organizations with issue types enabled. In this case, an organization scoped PAT is required.
     - No
     - :obj:`False`

