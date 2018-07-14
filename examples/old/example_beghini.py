from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.numerical.utilities import set_array_print_precision

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.viewers import Viewer

import compas_ags.ags.graphstatics as gs


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


set_array_print_precision('6f')


form = FormDiagram()

form.add_vertex(x=0., y=0.)  # 0
form.add_vertex(x=1., y=0.)  # 1
form.add_vertex(x=2., y=0.)  # 2
form.add_vertex(x=3., y=0.)  # 3
form.add_vertex(x=4., y=0.)  # 4
form.add_vertex(x=5., y=0.)  # 5
form.add_vertex(x=6., y=0.)  # 6

form.add_vertex(x=1., y=1.)  # 7
form.add_vertex(x=2., y=2.)  # 8
form.add_vertex(x=3., y=3.)  # 9
form.add_vertex(x=4., y=2.)  # 10
form.add_vertex(x=5., y=1.)  # 11

form.add_vertex(x=-1., y=0.)
form.add_vertex(x=0., y=-1.)
form.add_vertex(x=6., y=-1.)

form.add_vertex(x=1., y=-1.)
form.add_vertex(x=2., y=-1.)
form.add_vertex(x=3., y=-1.)
form.add_vertex(x=4., y=-1.)
form.add_vertex(x=5., y=-1.)

form.add_edge(0, 1)
form.add_edge(1, 2)
form.add_edge(2, 3)
form.add_edge(3, 4)
form.add_edge(4, 5)
form.add_edge(5, 6)

form.add_edge(0, 7)
form.add_edge(7, 8)
form.add_edge(8, 9)
form.add_edge(9, 10)
form.add_edge(10, 11)
form.add_edge(11, 6)

form.add_edge(1, 7)
form.add_edge(2, 8)
form.add_edge(3, 9)
form.add_edge(4, 10)
form.add_edge(5, 11)

form.add_edge(12, 0)
form.add_edge(13, 0)
form.add_edge(14, 6)

form.add_edge(1, 15)
form.add_edge(2, 16)
form.add_edge(3, 17)
form.add_edge(4, 18)
form.add_edge(5, 19)

form.identify_fixed()

force = ForceDiagram.from_formdiagram(form)

k, m = gs.count_dof(form)

ind = [2]

index_uv = form.index_uv()
for index in ind:
    u, v = index_uv[index]
    form.edge[u][v]['is_ind'] = True
    form.edge[u][v]['q'] = -10.

form.vertex[0]['is_fixed'] = True
form.vertex[6]['is_fixed'] = True

# force.vertex['0']['is_fixed'] = True


gs.update_forcedensity(form)
gs.update_forcediagram(force, form)

# force.vertex['1']['x'] -= 5.0

# ags.update_formdiagram(form, force, kmax=200)

# ------------------------------------------------------------------------------
# view
# ------------------------------------------------------------------------------

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())},
                 forcescale=2,
                 vertexsize=0.15)

viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                  edgelabel={uv: index for index, uv in enumerate(force.edges())},
                  vertexsize=0.15)

viewer.show()
