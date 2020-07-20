import compas
import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.viewers import Viewer

from compas_ags.ags import graphstatics
from compas_ags.ags import loadpath

# ------------------------------------------------------------------------------
# 1. create a planar truss structure, its applied loads and boundary conditions
#    from nodes and edges
#    make form and force diagrams
# ------------------------------------------------------------------------------

nodes = [
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
    [5.0, +1.0, 0]]

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
    (5, 18)]

graph = FormGraph.from_nodes_and_edges(nodes, edges)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
# 2. assign applied loads to bottom chord
# ------------------------------------------------------------------------------

edges = [(8, 1), (9, 2), (10, 3), (11, 4), (12, 5)]

for edge in edges:
    form.edge_attribute(edge, 'is_ind', True)
    form.edge_attribute(edge, 'q', 1.0)

# update force densities of form and force diagram
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# ------------------------------------------------------------------------------
# 3. optimize the loadpath
# ------------------------------------------------------------------------------

# modify force in the truss by updating vertex coordinates of the force diagram
# force in members of the top chord and bottom chord are set to be the same
# now the form is no longer in equilibrium
force.vertex_attributes(1, 'xy', [0, 2.5])
force.vertex_attributes(2, 'xy', [0, 1.5])
force.vertex_attributes(3, 'xy', [0, 0.5])
force.vertex_attributes(0, 'xy', [0, 0])
force.vertex_attributes(4, 'xy', [0, -0.5])
force.vertex_attributes(5, 'xy', [0, -1.5])
force.vertex_attributes(6, 'xy', [0, -2.5])

force.vertex_attributes(12, 'xy', [-2, 2.5])
force.vertex_attributes(11, 'xy', [-2, 1.5])
force.vertex_attributes(10, 'xy', [-2, 0.5])
force.vertex_attributes(9, 'xy', [-2, -0.5])
force.vertex_attributes(8, 'xy', [-2, -1.5])
force.vertex_attributes(7, 'xy', [-2, -2.5])

# forces in members of top chord and connecting struts are force domain parameters
force.vertices_attribute('is_param', True, keys=[7, 8, 9, 10, 11, 12])

# fix boundary vertices, the nodes of the bottom chord
form.vertices_attribute('is_fixed', True, keys=[0, 1, 2, 3, 4, 5, 6])

# optimize the loadpath and output the optimal distribution of forces that
# results in overall minimum-volumn solution for given form diagram
loadpath.optimise_loadpath(form, force)

# ------------------------------------------------------------------------------
# 4. display force and form diagrams
# ------------------------------------------------------------------------------

viewer = Viewer(form, force, delay_setup=False, figsize=(12, 7.5))

viewer.draw_form(
    forcescale=5,
    vertexlabel={key: str(key) for key in form.vertices()},
    vertexsize=0.2)
viewer.draw_force(
    vertexlabel={key: str(key) for key in force.vertices()},
    vertexsize=0.2)

viewer.show()
