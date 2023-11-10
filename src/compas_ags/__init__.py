"""
********************************************************************************
compas_ags
********************************************************************************

.. currentmodule:: compas_ags

.. toctree::
    :maxdepth: 1

    compas_ags.ags
    compas_ags.diagrams
    compas_ags.viewers

"""

import os

HERE = os.path.abspath(os.path.dirname(__file__))
HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.join(HOME, "data")
TEMP = os.path.join(HOME, "temp")


__author__ = "Tom Van Mele and others (see AUTHORS.md)"
__copyright__ = "Copyright 2014-2018 - Block Research Group, ETH Zurich"
__license__ = "MIT License"
__email__ = "vanmelet@ethz.ch"
__version__ = "1.2.1"


def get(relpath):
    return os.path.join(DATA, relpath)


__all__ = ["HOME", "DATA", "DOCS", "TEMP"]

__all_plugins__ = [
    "compas_ags.rhino.install",
]
