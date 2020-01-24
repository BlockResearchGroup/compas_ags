import compas
import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.viewers import Viewer

from compas_ags.ags import graphstatics
from compas_ags.ags import loadpath


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

graph = FormGraph.from_vertices_and_edges(vertices, edges)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

index_uv = form.index_uv()

ind = [3, 6, 10, 13, 16]

for index in ind:
    u, v = index_uv[index]
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', 1.0)

graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

force.vertex_attributes(7, 'xy', [0, 0])
force.vertex_attributes(8, 'xy', [0, 2.5])
force.vertex_attributes(13, 'xy', [0, -2.5])
force.vertex_attributes(6, 'xy', [-2, 2.5])
force.vertex_attributes(1, 'xy', [-2, -2.5])
force.vertex_attributes(9, 'xy', [0, 1.5])
force.vertex_attributes(12, 'xy', [0, -1.5])
force.vertex_attributes(5, 'xy', [-2, 1.5])
force.vertex_attributes(2, 'xy', [-2, -1.5])
force.vertex_attributes(10, 'xy', [0, 0.5])
force.vertex_attributes(11, 'xy', [0, -0.5])
force.vertex_attributes(4, 'xy', [-2, 0.5])
force.vertex_attributes(3, 'xy', [-2, -0.5])

force.vertices_attribute('is_param', True, keys=[1, 2, 3, 4, 5, 6])
form.vertices_attribute('is_fixed', True, keys=[0, 1, 2, 3, 4, 5, 6])

graphstatics.form_update_from_force(form, force)
loadpath.optimise_loadpath(form, force)

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(forcescale=5, vertexlabel={key: key for key in form.vertices()}, vertexsize=0.2)
viewer.draw_force(vertexlabel={key: key for key in force.vertices()}, vertexsize=0.2)

# viewer.save('C:\\Users\\tomvm\\Code\\__temp\\lpopt.png', dpi=300)
viewer.show()
