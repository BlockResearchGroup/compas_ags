"""
********************************************************************************
compas_ags.rhino
********************************************************************************

.. currentmodule:: compas_ags.rhino

Artists
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    DiagramArtist
    FormArtist
    ForceArtist

Objects
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    FormObject

Scenes
======

.. autosummary::
    :toctree: generated/
    :nosignatures:

"""
from __future__ import absolute_import

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from .diagramartist import DiagramArtist
from .formartist import FormArtist
from .forceartist import ForceArtist

from .formobject import FormObject

from .scene import Scene
from .scene import SceneObject


SceneObject.register(FormDiagram, FormObject, FormArtist)


__all__ = [name for name in dir() if not name.startswith('_')]
