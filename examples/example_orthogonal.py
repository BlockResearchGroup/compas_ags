from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import random

import compas
import compas_ags

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.viewers import Viewer

from compas_ags.ags import graphstatics as gs


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


form = FormDiagram.from_obj(compas.get('lines.obj'))
force = ForceDiagram.from_formdiagram(form)

for key, attr in form.vertices_where({'vertex_degree': 1}, True):
    attr['is_fixed'] = True

k, m, ind = gs.identify_dof(form)

print(k, m, ind)

for index, (u, v, attr) in enumerate(form.edges(True)):
    if index in ind:
        attr['is_ind'] = True
        attr['q'] = random.choice(range(1, 20))

gs.update_forcedensity(form)
gs.update_forcediagram(force, form)

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(
    vertexsize=0.15,
    vertexlabel={key: key for key in form.vertices()},
    edgelabel={uv: index for index, uv in enumerate(form.edges())},
    external_on=False
)

viewer.draw_force(
    vertexsize=0.15,
    vertexlabel={key: key for key in force.vertices()}
)

viewer.show()
