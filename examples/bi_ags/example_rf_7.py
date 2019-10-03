"""Example from Fig. 7 in the paper. Modify the force diagram of
a simple arch with constraints by moving the vertices furthest
to the left past the vertices furthest to the right and compute
the form diagram using Newton's method.

author: Vedad Alic
email: vedad.alic@construction.lth.se

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.diagrams import FormDiagram
from compas_bi_ags.diagrams import ForceDiagram
from compas_ags.viewers import Viewer
from compas_bi_ags.bi_ags import graphstatics

edges = [
        (0, 10),
        (1, 9),
        (2, 11),
        (3, 2),
        (4, 12),
        (5, 13),
        (6, 14),
        (7, 15),
        (8, 16),
        (2, 0),
        (0, 8),
        (8, 7),
        (7, 6),
        (6, 5),
        (5, 4),
        (4, 9),
        (9, 17),
]

vertices = [
[ 3.62477467512, 2.99447312681,  0.0],
[ 43.4972961014, -7.27758178128, 0.0],
[ 0.0,           0.0,            0.0],
[ 0.0,           -7.27758178128, 0.0],
[ 39.8725214263, 2.99447312681,  0.0],
[ 32.6229720760, 6.81140730234,  0.0],
[ 25.3734227258, 8.54514654776,  0.0],
[ 18.1238733756, 8.54514654776,  0.0],
[ 10.8743240253, 6.81140730234,  0.0],
[ 43.4972961014, 0.0,            0.0],
[ 3.62477467512, 10.2720549081,  0.0],
[-3.52953624469, 0.0,            0.0],
[ 39.8725214263, 10.2720549081,  0.0],
[ 32.6229720760, 14.0889890836,  0.0],
[ 25.3734227258, 15.8227283290,  0.0],
[ 18.1238733756, 15.8227283290,  0.0],
[ 10.8743240253, 14.0889890836,  0.0],
[ 47.4502140636, 0.0,            0.0],
]

form = FormDiagram.from_vertices_and_edges(vertices, edges)
force = ForceDiagram.from_formdiagram(form)

edges_ind = [
            (2, 11),
]

for index in edges_ind:
    u, v = index
    form.edge[u][v]['is_ind'] = True
    form.edge[u][v]['q'] = -1.


# set the fixed points
left  = list(form.vertices_where({'x': 0.0, 'y': 0.0}))[0]
right = list(form.vertices_where({'x': 43.4972961014, 'y': 0.0}))[0]
fixed = [left, right]

form.set_fixed(fixed)
force.set_anchor([5])

graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

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
# Begin force diagram manipulation
# --------------------------------------------------------------------------
import numpy as np
_xy = np.array(force.xy(), dtype=np.float64).reshape((-1, 2))
_x_min = min(_xy[:,0])

move_vertices = []
for i, v in enumerate(_xy):
    if v[0] > (_x_min-.1) and v[0] < (_x_min+.1):
       move_vertices.append(i)


from compas_bi_ags.bi_ags.constraints import ConstraintsCollection, HorizontalFix, VerticalFix
C = ConstraintsCollection(form)
C.add_constraint(HorizontalFix(form, left))
C.add_constraint(VerticalFix(form, left))
C.add_constraint(HorizontalFix(form, right))
C.add_constraint(HorizontalFix(form, 0))
C.add_constraint(HorizontalFix(form, 4))
C.add_constraint(HorizontalFix(form, 5))
C.add_constraint(HorizontalFix(form, 6))
C.add_constraint(HorizontalFix(form, 7))
C.add_constraint(HorizontalFix(form, 8))
C.constrain_dependent_leaf_edges_lengths()

import compas_bi_ags.bi_ags.rootfinding as rf
xy = np.array(form.xy(), dtype=np.float64).reshape((-1, 2))
_xy = np.array(force.xy(), dtype=np.float64).reshape((-1, 2))
_xy[move_vertices, 0] += 6
_X_goal = np.vstack((np.asmatrix(_xy[:, 0]).transpose(), np.asmatrix(_xy[:, 1]).transpose()))
rf.compute_form_from_force_newton(form, force, _X_goal, constraints=C)
constraint_lines = C.get_lines()
# --------------------------------------------------------------------------
# End force diagram manipulation
# --------------------------------------------------------------------------

form_lines = form_lines + constraint_lines

# display the original configuration
# and the configuration after modifying the force diagram
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