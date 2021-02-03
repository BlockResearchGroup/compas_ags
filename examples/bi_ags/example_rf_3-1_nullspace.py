"""Compute the null space of the Jacobian matrix dX*/dX.

author: Vedad Alic
email: vedad.alic@construction.lth.se

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.viewers import Viewer
from compas_ags.ags import graphstatics

from compas_ags.ags import compute_nullspace
from compas_ags.ags import ConstraintsCollection, HorizontalFix, VerticalFix, AngleFix


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

for key in fixed:
    form.vertex_attribute(key, 'is_fixed', True)
form.vertex_attribute(key, 'is_anchor', True)

# ------------------------------------------------------------------------------
#   3. set applied load
# ------------------------------------------------------------------------------
e1 ={'v': list(form.vertices_where({'x': 3.0, 'y': 3.0}))[0],
     'u': list(form.vertices_where({'x': 3.669563106796117, 'y': 5.008689320388349}))[0]}
form.edge_attribute((e1['v'], e1['u']), 'q', -1.0)
form.edge_attribute((e1['v'], e1['u']), 'is_ind', True)

# update the diagrams
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# store the original vertex locations
force_key_xyz = {key: force.vertex_coordinates(key) for key in force.vertices()}


# --------------------------------------------------------------------------
#   4. force diagram manipulation and ompute the nullspace
# --------------------------------------------------------------------------
# set constraints
C = ConstraintsCollection(form)

# fix an angle to left and right vertices
C.add_constraint(AngleFix(form, left, 30))
C.add_constraint(AngleFix(form, right, 30))

# fix the length of edges connecting leaf vertices
C.constrain_dependent_leaf_edges_lengths()
constraint_lines = C.get_lines()

# compute the amount of nullspace modes
# which means the amount of independent solutions of form diagrams
ns = compute_nullspace(form, force, C)
print("Dimension of nullspace: " + str(len(ns)))


# --------------------------------------------------------------------------
#   5. display force diagram and a specific solution of form diagram
# --------------------------------------------------------------------------
def show(i):
    # i is the index of nullspace mode
    c = 10
    c += 1
    nsi = ns[i] * c
    # store lines representing the current null space mode
    form_lines = []
    for u, v in form.edges():
        form_lines.append({
            'start': [x + y for x, y in zip(form.vertex_coordinates(u, 'xy'),  nsi[u])],
            'end'  : [x + y for x, y in zip(form.vertex_coordinates(v, 'xy'),  nsi[v])],
            'width': 1.0,
            'color': '#cccccc',
            'style': '--'
        })


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

    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                      vertexsize=0.2,
                      edgelabel={uv: index for index, uv in enumerate(force.edges())}
    )

    viewer.show()

show(0)
