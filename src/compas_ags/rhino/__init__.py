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
from compas_ags.diagrams import ForceDiagram  # noqa: F401

from .diagramartist import DiagramArtist  # noqa: F401
from .formartist import FormArtist
from .forceartist import ForceArtist  # noqa: F401

from .formobject import FormObject

from .scene import Scene  # noqa: F401
from .scene import SceneObject


SceneObject.register(FormDiagram, FormObject, FormArtist)


__all__ = [name for name in dir() if not name.startswith('_')]
