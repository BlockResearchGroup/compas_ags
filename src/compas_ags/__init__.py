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
HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.join(HOME, 'data')
TEMP = os.path.join(HOME, 'temp')


def get(relpath):
    return os.path.join(DATA, relpath)


__all__ = []
