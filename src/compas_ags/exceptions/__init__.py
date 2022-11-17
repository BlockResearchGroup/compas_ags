"""
********************************************************************************
compas_ags.exceptions
********************************************************************************

.. currentmodule:: compas_ags.exceptions


Classes
=======

.. autosummary::
    :toctree: generated/

    SolutionError


"""
from __future__ import absolute_import

from .errorhandler import *  # noqa: F401 F403

__all__ = [name for name in dir() if not name.startswith("_")]
