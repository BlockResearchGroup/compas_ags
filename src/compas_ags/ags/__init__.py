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
    update_form_from_force


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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if compas.IPY:
    from .graphstatics import form_identify_dof_proxy
    from .graphstatics import form_count_dof_proxy
    from .graphstatics import form_update_q_from_qind_proxy
    from .graphstatics import form_update_from_force_proxy
else:
    from .graphstatics import *

__all__ = [name for name in dir() if not name.startswith('_')]
