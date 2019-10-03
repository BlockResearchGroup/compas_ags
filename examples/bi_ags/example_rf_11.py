"""Example from Fig. 11 in the paper. Modify the force diagram of
a post tensioned funicular structure with constraints and compute
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
        (0,  11),
        (1,  10),
        (2,  13),
        (3,  12),
        (4,  7),
        (5,  8),
        (3,  2),
        (6,  7),
        (7,  8),
        (8,  2),
        (0,  3),
        (1,  0),
        (9,  1),
        (10, 16),
        (11, 17),
        (12, 18),
        (13, 19),
        (5,  20),
        (4,  21),
        (14, 9),
        (9,  22),
        (15, 6),
        (9,  10),
        (10, 11),
        (11, 12),
        (12, 13),
        (13, 5),
        (5,  4),
        (4,  6),
        (6,  23),
]

vertices = [
    [10.9336764457,  2.93969333667,  0.0],
    [4.27834823297,  0.934076623109, 0.0],
    [22.9483377430,  3.56198575470,  0.0],
    [17.0516622570,  3.56198575470,  0.0],
    [36.6666666667,  2.75370967411,  0.0],
    [30.0,           6.26375238264,  0.0],
    [40.0,           0.0,            0.0],
    [35.7216517670,  0.934076623109, 0.0],
    [29.0663235543,  2.93969333667,  0.0],
    [0.0,            0.0,            0.0],
    [3.33333333333,  2.75370967411,  0.0],
    [10.0,           6.26375238264,  0.0],
    [16.6666666667,  7.85809446899,  0.0],
    [23.3333333333,  7.85809446899,  0.0],
    [0.0,            -6.69244521712, 0.0],
    [40.0,           -6.69244521712, 0.0],
    [3.33333333333,  9.44615489123,  0.0],
    [10.0,           12.9561975998,  0.0],
    [16.6666666667,  14.5505396861,  0.0],
    [23.3333333333,  14.5505396861,  0.0],
    [30.0,           12.9561975998,  0.0],
    [36.6666666667,  9.44615489123,  0.0],
    [-3.24575232121, 0.0,            0.0],
    [43.6350930439,  0.0,            0.0],
]

form = FormDiagram.from_vertices_and_edges(vertices, edges)
force = ForceDiagram.from_formdiagram(form)

edges_ind = [
    (9,  22),
    (10, 16),
]
for index in edges_ind:
    u, v = index
    form.edge[u][v]['is_ind'] = True
    form.edge[u][v]['q'] = -1.

# set the fixed points
left  = list(form.vertices_where({'x': 0.0, 'y': 0.0}))[0]
right = list(form.vertices_where({'x': 40., 'y': 0.0}))[0]
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
    if v[0] > (_x_min-.1) and v[0] < (_x_min+1):
       move_vertices.append(i)


from compas_bi_ags.bi_ags.constraints import ConstraintsCollection, HorizontalFix, VerticalFix
C = ConstraintsCollection(form)
C.add_constraint(HorizontalFix(form, left))
C.add_constraint(VerticalFix(form, left))
C.add_constraint(HorizontalFix(form, right))
C.add_constraint(VerticalFix(form, right))
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