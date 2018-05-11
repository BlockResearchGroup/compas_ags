from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import json
import os

import compas_ags

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.viewers import Viewer

import compas_ags.ags.graphstatics as gs
import compas_ags.ags.loadpath as lpopt


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


vertices = [
    [0.0, 0.0, 0],
    [1.0, 0.0, 0],
    [2.0, 0.0, 0],
    [3.0, 0.0, 0],
    [4.0, 0.0, 0],
    [5.0, 0.0, 0],
    [6.0, 0.0, 0],

    [0.0, -1.0, 0],
    [1.0, -1.0, 0],
    [2.0, -1.0, 0],
    [3.0, -1.0, 0],
    [4.0, -1.0, 0],
    [5.0, -1.0, 0],
    [6.0, -1.0, 0],

    [1.0, +1.0, 0],
    [2.0, +1.0, 0],
    [3.0, +1.0, 0],
    [4.0, +1.0, 0],
    [5.0, +1.0, 0],
]

edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6),

    (0, 7),
    (1, 8),
    (2, 9),
    (3, 10),
    (4, 11),
    (5, 12),
    (6, 13),

    (0, 14),
    (14, 15),
    (15, 16),
    (16, 17),
    (17, 18),
    (18, 6),

    (1, 14),
    (2, 15),
    (3, 16),
    (4, 17),
    (5, 18),
]

form = FormDiagram.from_vertices_and_edges(vertices, edges)
force = ForceDiagram.from_formdiagram(form)

index_uv = form.index_uv()

ind = [3, 6, 10, 13, 16]

for index in ind:
    u, v = index_uv[index]
    form.edge[u][v]['is_ind'] = True
    form.edge[u][v]['q'] = 1.

gs.update_forcedensity(form)

gs.update_forcediagram(force, form)

force.vertex[7]['x']  = 0
force.vertex[7]['y']  = 0

force.vertex[8]['x']  = 0
force.vertex[8]['y']  = 2.5
force.vertex[13]['x'] = 0
force.vertex[13]['y'] = -2.5

force.vertex[6]['x']  = -2
force.vertex[6]['y']  = 2.5
force.vertex[1]['x']  = -2
force.vertex[1]['y']  = -2.5

force.vertex[9]['x']  = 0
force.vertex[9]['y']  = 1.5
force.vertex[12]['x'] = 0
force.vertex[12]['y'] = -1.5

force.vertex[5]['x']  = -2
force.vertex[5]['y']  = 1.5
force.vertex[2]['x']  = -2
force.vertex[2]['y']  = -1.5

force.vertex[10]['x'] = 0
force.vertex[10]['y'] = 0.5
force.vertex[11]['x'] = 0
force.vertex[11]['y'] = -0.5

force.vertex[4]['x']  = -2
force.vertex[4]['y']  = 0.5
force.vertex[3]['x']  = -2
force.vertex[3]['y']  = -0.5

force.vertex[1]['is_param'] = True
force.vertex[2]['is_param'] = True
force.vertex[3]['is_param'] = True
force.vertex[4]['is_param'] = True
force.vertex[5]['is_param'] = True
force.vertex[6]['is_param'] = True

form.vertex[0]['is_fixed'] = True
form.vertex[1]['is_fixed'] = True
form.vertex[2]['is_fixed'] = True
form.vertex[3]['is_fixed'] = True
form.vertex[4]['is_fixed'] = True
form.vertex[5]['is_fixed'] = True
form.vertex[6]['is_fixed'] = True

gs.update_formdiagram(form, force)


with open(os.path.join(compas_ags.DATA, 'form_lpopt.json'), 'w+') as fp:
    data = form.to_data()
    json.dump({'form': data}, fp)


lpopt.optimise_loadpath(form, force)


viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(forcescale=5, vertexlabel={key: key for key in form.vertices()}, vertexsize=0.2)
viewer.draw_force(vertexlabel={key: key for key in force.vertices()}, vertexsize=0.2)

viewer.show()
