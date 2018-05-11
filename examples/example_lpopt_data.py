from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import json

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


with open(compas_ags.get('form_lpopt.json'), 'r') as fp:
    data = json.load(fp)


form = FormDiagram.from_data(data['form'])
force = ForceDiagram.from_formdiagram(form)

gs.update_forcedensity(form)
gs.update_forcediagram(force, form)

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

form_lines = []
for u, v in form.edges():
    form_lines.append({
        'start': form.vertex_coordinates(u, 'xy'),
        'end'  : form.vertex_coordinates(v, 'xy'),
        'width': 2.0,
        'color': '#cccccc',
        'style': '--'
    })

force_lines = []
for u, v in force.edges():
    force_lines.append({
        'start': force.vertex_coordinates(u, 'xy'),
        'end'  : force.vertex_coordinates(v, 'xy'),
        'width': 2.0,
        'color': '#cccccc',
        'style': '--'
    })

lpopt.optimise_loadpath(form, force)

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(forcescale=5, lines=form_lines)
viewer.draw_force(vertexlabel={key: key for key in force.vertices()}, lines=force_lines)

viewer.show()
