"""
********************************************************************************
compas_tna.rhino
********************************************************************************

.. currentmodule:: compas_tna.rhino

Helpers
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:


Artists
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    FormArtist
    ForceArtist

"""
from __future__ import absolute_import

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from .formartist import FormArtist
from .forceartist import ForceArtist

from .formobject import FormObject

from .scene import Scene
from .scene import SceneObject


SceneObject.register(FormDiagram, FormObject, FormArtist)


__all__ = [name for name in dir() if not name.startswith('_')]
