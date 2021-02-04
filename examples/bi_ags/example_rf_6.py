"""Example from Fig. 11 in the paper. Modify the force diagram of
a post tensioned funicular structure with constraints and compute
the form diagram using Newton's method.

author: Vedad Alic
email: vedad.alic@construction.lth.se

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np

import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.viewers import Viewer
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import ConstraintsCollection
from compas_ags.ags import form_update_from_force_newton

# ------------------------------------------------------------------------------
#   1. create a funicular structure from nodes and edges, make form and force diagrams
# ------------------------------------------------------------------------------

graph = FormGraph.from_json(compas_ags.get('paper/gs_arch_2layers.json'))
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
#   2. prescribe edge force density and set fixed vertices
# ------------------------------------------------------------------------------
edges_ind = [
    (9,  22),
    (10, 16),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', -1.)

# set the fixed points
left = list(form.vertices_where({'x': 0.0, 'y': 0.0}))[0]
right = list(form.vertices_where({'x': 40., 'y': 0.0}))[0]
fixed = [left, right]
for key in fixed:
    form.vertex_attribute(key, 'is_fixed', True)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# store lines representing the current state of equilibrium
form_lines = []
for u, v in form.edges():
    form_lines.append({
        'start': form.vertex_coordinates(u, 'xy'),
        'end': form.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

force_lines = []
for u, v in force.edges():
    force_lines.append({
        'start': force.vertex_coordinates(u, 'xy'),
        'end': force.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })


# --------------------------------------------------------------------------
#   3. force diagram manipulation and modify the form diagram
# --------------------------------------------------------------------------
# set constraints
_xy = np.array(force.xy(), dtype=np.float64).reshape((-1, 2))
_x_min = min(_xy[:, 0])

move_vertices = []
for i, v in enumerate(_xy):
    if v[0] > (_x_min-.1) and v[0] < (_x_min+1):
        move_vertices.append(i)

C = ConstraintsCollection(form)
C.constraints_from_form()

# modify the geometry of the force diagram and update the form diagram using Newton's method
xy = np.array(form.xy(), dtype=np.float64).reshape((-1, 2))
_xy = np.array(force.xy(), dtype=np.float64).reshape((-1, 2))
_xy[move_vertices, 0] += 6
_X_goal = np.vstack((np.asmatrix(_xy[:, 0]).transpose(), np.asmatrix(_xy[:, 1]).transpose()))
form_update_from_force_newton(form, force, _X_goal, constraints=C)

constraint_lines = C.get_lines()
form_lines = form_lines + constraint_lines


# ------------------------------------------------------------------------------
#   4. display the orginal configuration
#      and the configuration after modifying the force diagram
# ------------------------------------------------------------------------------
viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(lines=form_lines,
                 forces_on=False,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=False,
                 vertexsize=0.2,
                 vertexcolor={key: '#000000' for key in fixed},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())}
                 )

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel={uv: index for index, uv in enumerate(force.edges())}
                  )

viewer.show()
