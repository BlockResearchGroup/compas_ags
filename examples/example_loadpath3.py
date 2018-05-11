from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.viewers import Viewer

import compas_ags.ags.graphstatics as gs
import compas_ags.ags.thrustdiagrams as gs3


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


form = FormDiagram.from_obj(compas.get('lines.obj'))
form.identify_fixed()

force = ForceDiagram.from_formdiagram(form)

k, m, ind = gs.identify_dof(form, indexed=False)

count = 1
for u, v in ind:
    form.edge[u][v]['is_ind'] = True
    form.edge[u][v]['q'] = 1.0 * count
    count += 1

for key, attr in form.vertices_iter(True):
    attr['px'] = 0.0
    attr['py'] = 0.0
    attr['pz'] = 1.0

gs.update_forcedensity(form)
gs.update_forcediagram(force, form)

gs3.update_thrustdiagram(form, force)


viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form()
viewer.draw_force()

viewer.show()
