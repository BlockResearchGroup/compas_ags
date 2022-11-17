"""
********************************************************************************
compas_ags.ags
********************************************************************************

.. currentmodule:: compas_ags.ags


Core
====

.. autosummary::
    :toctree: generated/

    update_q_from_qind
    update_primal_from_dual


Graph Statics
=============

.. autosummary::
    :toctree: generated/

    form_count_dof
    form_identify_dof
    form_update_q_from_qind
    form_update_from_force
    force_update_from_form


Load Path
=========

.. autosummary::
    :toctree: generated/

    compute_loadpath
    compute_external_work
    compute_internal_work
    compute_internal_work_tension
    compute_internal_work_compression
    optimise_loadpath

"""
from __future__ import absolute_import

import compas

if not compas.IPY:
    from .core import *  # noqa: F401 F403
    from .graphstatics import *  # noqa: F401 F403
    from .loadpath import *  # noqa: F401 F403
    from .constraints import *  # noqa: F401 F403

__all__ = [name for name in dir() if not name.startswith("_")]
