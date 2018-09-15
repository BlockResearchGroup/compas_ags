********************************************************************************
Contributions
********************************************************************************

.. language:: bash


Code contributions
==================

We accept code contributions through pull requests.
In short, this is how that works.

1. Fork a copy of the `the compas_ags repository <https://github.com/compas-dev/compas_ags>`_ to your account and clone the fork to your computer.
2. Create a virtual environment using your tool of choice (e.g. ``virtualenv``, ``conda``, etc).
3. Install development dependencies:

::

    $ pip install -r requirements-dev.txt


4. Make a branch for your contribution using a descriptive name.
5. Make the required changes to the code of the branch.
6. Add yourself to ``CONTRIBUTORS.md``.
7. Commit your changes and push your branch to GitHub.
8. Create a `pull request <https://help.github.com/articles/about-pull-requests/>`_ through the GitHub website.


During development, use `pyinvoke <http://docs.pyinvoke.org/>`_ tasks on the
command line to ease recurring operations:

* ``invoke clean``: Clean all generated artifacts.
* ``invoke check``: Run various code and documentation style checks.
* ``invoke docs``: Generate documentation.
* ``invoke``: Show available tasks.


Bug reports
===========

When `reporting a bug <https://github.com/compas-dev/compas/issues>`_
please include:

    * Operating system name and version.
    * Any details about your local setup that might be helpful in troubleshooting.
    * Detailed steps to reproduce the bug.


Feature requests and feedback
=============================

The best way to send feedback is to file an issue on
`Github <https://github.com/compas-dev/compas/issues>`_.
If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
