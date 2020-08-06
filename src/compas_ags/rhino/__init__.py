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
    BaseArtist

Objects
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    DiagramObject
    FormObject
    ForceObject
    BaseObject


Scene
=====

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Scene

"""
from __future__ import absolute_import

from compas_ags.diagrams import FormDiagram  # noqa: F401
from compas_ags.diagrams import ForceDiagram  # noqa: F401
from compas_ags.diagrams import BaseDiagram  # noqa: F401

from .diagramartist import DiagramArtist  # noqa: F401
from .formartist import FormArtist  # noqa: F401
from .forceartist import ForceArtist  # noqa: F401
from .baseartist import BaseArtist  # noqa: F401

from .diagramobject import DiagramObject  # noqa: F401
from .formobject import FormObject  # noqa: F401
from .forceobject import ForceObject  # noqa: F401
from .baseobject import BaseObject  # noqa: F401

from .scene import Scene  # noqa: F401

DiagramArtist.register(FormDiagram, FormArtist)
DiagramArtist.register(ForceDiagram, ForceArtist)
DiagramArtist.register(BaseDiagram, BaseArtist)

DiagramObject.register(FormDiagram, FormObject)
DiagramObject.register(ForceDiagram, ForceObject)
DiagramObject.register(BaseDiagram, BaseObject)

__all__ = [name for name in dir() if not name.startswith('_')]
