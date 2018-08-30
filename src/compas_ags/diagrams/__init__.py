"""
********************************************************************************
diagrams
********************************************************************************

.. currentmodule:: compas_ags.diagrams


.. autosummary::
    :toctree: generated/

    FormDiagram
    ForceDiagram

"""

from compas_ags.diagrams import formdiagram
from compas_ags.diagrams import forcediagram

from .formdiagram import *
from .forcediagram import *

__all__ = formdiagram.__all__ + forcediagram.__all__
