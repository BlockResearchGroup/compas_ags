from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_ags

from compas_ags.diagrams import FormDiagram
from compas_bi_ags.diagrams import ForceDiagram

from compas_ags.viewers import Viewer

from compas_bi_ags.bi_ags import graphstatics


__author__    = ['Vedad Alic', ]
__license__   = 'MIT License'
__email__     = 'vedad.alic@construction.lth.se'


__all__ = []


# make form diagram from obj
# make force diagram from form
form = FormDiagram.from_obj(compas_ags.get('paper/gs_form_force.obj'))
force = ForceDiagram.from_formdiagram(form)

# set the fixed points
left  = list(form.vertices_where({'x': 0.0, 'y': 0.0}))[0]
right = list(form.vertices_where({'x': 6.0, 'y': 0.0}))[0]
fixed = [left, right]

form.set_fixed(fixed)
force.set_anchor([5])

# set the magnitude of the applied load
#form.set_edge_force_by_index(0, -10.0)
e1 ={'v': list(form.vertices_where({'x': 3.0, 'y': 3.0}))[0],
     'u': list(form.vertices_where({'x': 3.669563106796117, 'y': 5.008689320388349}))[0]}
form.set_edge_forcedensity(e1['v'], e1['u'], -1.0)

# update the diagrams
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# store the original vertex locations
force_key_xyz = {key: force.vertex_coordinates(key) for key in force.vertices()}




# --------------------------------------------------------------------------
# Begin force diagram manipulation
# --------------------------------------------------------------------------
from compas_bi_ags.bi_ags.constraints import ConstraintsCollection, HorizontalFix, VerticalFix, LengthFix
C = ConstraintsCollection(form)
C.add_constraint(HorizontalFix(form, left))
C.add_constraint(HorizontalFix(form, right))
C.constrain_free_leaf_edges_lengths()

import compas_bi_ags.bi_ags.rootfinding as rf
import numpy as np

ns = rf.compute_nullspace(form, force, C)

constraint_lines = C.get_lines()
# --------------------------------------------------------------------------
# End force diagram manipulation
# --------------------------------------------------------------------------



# --------------------------------------------------------------------------
# Draw diagrams and nullspace mode i
# --------------------------------------------------------------------------
def show(i):
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