"""Simple example to compute the form diagram after modifying the
force diagram with constraints. Solved using root finding with
Newton's method.

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
from compas_ags.ags import graphstatics

import compas_ags.ags2.rootfinding as rf
from compas_ags.ags2.constraints import ConstraintsCollection, HorizontalFix, VerticalFix


# ------------------------------------------------------------------------------
#   1. get lines of a plane triangle frame in equilibrium, its applied loads and reaction forces
# ------------------------------------------------------------------------------
graph = FormGraph.from_obj(compas_ags.get('paper/gs_form_force.obj'))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
#   2. set the fixed vertices
# ------------------------------------------------------------------------------
left  = list(form.vertices_where({'x': 0.0, 'y': 0.0}))[0]
right = list(form.vertices_where({'x': 6.0, 'y': 0.0}))[0]
fixed = [left, right]

form.set_fixed(fixed)
force.set_anchor([5])

# ------------------------------------------------------------------------------
#   3. set applied load
# ------------------------------------------------------------------------------
# set the magnitude of the applied load
e1 ={'v': list(form.vertices_where({'x': 3.0, 'y': 3.0}))[0],
     'u': list(form.vertices_where({'x': 3.669563106796117, 'y': 5.008689320388349}))[0]}
form.set_edge_forcedensity(e1['v'], e1['u'], -1.0)

# update the diagrams
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# store the original vertex locations
force_key_xyz = {key: force.vertex_coordinates(key) for key in force.vertices()}

# store lines representing the current state of equilibrium
form_lines = []
for u, v in form.edges():
    form_lines.append({
        'start': form.vertex_coordinates(u, 'xy'),
        'end'  : form.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

force_lines = []
for u, v in force.edges():
    force_lines.append({
        'start': force.vertex_coordinates(u, 'xy'),
        'end'  : force.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })


# --------------------------------------------------------------------------
#   4. force diagram manipulation and modify the form diagram
# --------------------------------------------------------------------------
# set constraints
C = ConstraintsCollection(form)
# fix x and y coordinates of the left and right vertices
C.add_constraint(HorizontalFix(form, left))
C.add_constraint(VerticalFix(form, left))
C.add_constraint(HorizontalFix(form, right))
C.add_constraint(VerticalFix(form, right))
# fix the length of edges connecting leaf vertices
C.constrain_dependent_leaf_edges_lengths()
constraint_lines = C.get_lines()

# modify the geometry of the force diagram and update the form diagram using Newton's method
xy = np.array(form.xy(), dtype=np.float64).reshape((-1, 2))
_xy = np.array(force.xy(), dtype=np.float64).reshape((-1, 2))
_xy[force.key_index()[3], 0] -= 0.5
_X_goal = np.vstack((np.asmatrix(_xy[:, 0]).transpose(), np.asmatrix(_xy[:, 1]).transpose()))
rf.compute_form_from_force_newton(form, force, _X_goal, constraints=C)

# add arrow to lines to indicate movement
force_lines.append({
    'start': force_key_xyz[3],
    'end': force.vertex_coordinates(3),
    'color': '#ff0000',
    'width': 10.0,
    'style': '-',
})

form_lines = form_lines + constraint_lines


# ------------------------------------------------------------------------------
#   5. display the orginal configuration
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
