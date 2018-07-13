from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_ags

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

import compas_ags.ags.graphstatics as gs
import compas_ags.ags.loadpath as lpopt


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


form = FormDiagram.from_obj(compas_ags.get('paper/gs_form_force.obj'))
form.identify_fixed()

force = ForceDiagram.from_formdiagram(form)

index_uv = form.index_uv()

k, m, ind = gs.identify_dof(form)

ind = [0]

for index in ind:
    u, v = index_uv[index]
    form.edge[u][v]['q'] = -3.
    form.edge[u][v]['is_ind'] = True

gs.update_forcedensity(form)
gs.update_forcediagram(force, form)

# ------------------------------------------------------------------------------
# view
# ------------------------------------------------------------------------------

print(lpopt.compute_external_work(form, force))
print(lpopt.compute_internal_work(form, force))

print(lpopt.compute_internal_work_tension(form, force))
print(lpopt.compute_internal_work_compression(form, force))
