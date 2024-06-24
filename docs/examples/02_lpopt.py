from compas_viewer import Viewer
from compas_viewer.config import Config

from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Circle
from compas.geometry import Polygon
from compas.geometry import bounding_box
from compas_ags.ags import graphstatics
from compas_ags.ags import loadpath
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import FormGraph

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

graph = FormGraph.from_nodes_and_edges(nodes, edges)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
# 2. assign applied loads to bottom chord
# ------------------------------------------------------------------------------

edges = [(8, 1), (9, 2), (10, 3), (11, 4), (12, 5)]

for edge in edges:
    form.edge_attribute(edge, "is_ind", True)
    form.edge_attribute(edge, "q", 1.0)

# update force densities of form and force diagram
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# ------------------------------------------------------------------------------
# 3. optimize the loadpath
# ------------------------------------------------------------------------------

# modify force in the truss by updating vertex coordinates of the force diagram
# force in members of the top chord and bottom chord are set to be the same
# now the form is no longer in equilibrium
force.vertex_attributes(1, "xy", [0, 2.5])
force.vertex_attributes(2, "xy", [0, 1.5])
force.vertex_attributes(3, "xy", [0, 0.5])
force.vertex_attributes(0, "xy", [0, 0])
force.vertex_attributes(4, "xy", [0, -0.5])
force.vertex_attributes(5, "xy", [0, -1.5])
force.vertex_attributes(6, "xy", [0, -2.5])

force.vertex_attributes(12, "xy", [-2, 2.5])
force.vertex_attributes(11, "xy", [-2, 1.5])
force.vertex_attributes(10, "xy", [-2, 0.5])
force.vertex_attributes(9, "xy", [-2, -0.5])
force.vertex_attributes(8, "xy", [-2, -1.5])
force.vertex_attributes(7, "xy", [-2, -2.5])

# forces in members of top chord and connecting struts are force domain parameters
force.vertices_attribute("is_param", True, keys=[7, 8, 9, 10, 11, 12])

# fix boundary vertices, the nodes of the bottom chord
form.vertices_attribute("is_fixed", True, keys=[0, 1, 2, 3, 4, 5, 6])

# optimize the loadpath and output the optimal distribution of forces that
# results in overall minimum-volumn solution for given form diagram
loadpath.optimise_loadpath(form, force)

# ------------------------------------------------------------------------------
# 4. display force and form diagrams
# ------------------------------------------------------------------------------

loadcolor = Color.green().darkened(50)
reactioncolor = Color.green().darkened(50)
tensioncolor = Color.red().lightened(25)
compressioncolor = Color.blue().lightened(25)

b1 = Box.from_bounding_box(bounding_box(form.vertices_attributes("xyz")))
b2 = Box.from_bounding_box(bounding_box(force.vertices_attributes("xyz")))

dx = b2.xmin - b1.xmax
if dx < 1:
    dx = 1.5 * (b1.xmax - b2.xmin)
else:
    dx = 0

config = Config()
config.renderer.view = "top"
config.renderer.gridsize = [100, 100, 100, 100]

viewer = Viewer(config=config)

viewer.scene.add(form, show_faces=False, show_lines=False, name="FormDiagram")
viewer.scene.add(force.translated([dx, 0, 0]), show_faces=False, name="ForceDiagram")

circles = [Circle.from_point_and_radius(form.vertex_point(vertex) + [0, 0, 0.001], 0.1).to_polygon(n=128) for vertex in form.vertices()]
viewer.scene.add(circles, name="Vertices", facecolor=Color.white(), linecolor=Color.black())

external = []
compression = []
tension = []
for edge in form.edges():
    line = form.edge_line(edge)
    vector = line.direction.cross([0, 0, 1])
    force = form.edge_attribute(edge, name="f")
    w = 0.01 * 0.5 * abs(force)
    a = line.start + vector * -w
    b = line.end + vector * -w
    c = line.end + vector * +w
    d = line.start + vector * +w
    if form.edge_attribute(edge, name="is_external"):
        external.append(Polygon([a, b, c, d]))
    elif force > 0:
        tension.append(Polygon([a, b, c, d]))
    elif force < 0:
        compression.append(Polygon([a, b, c, d]))

viewer.scene.add(external, name="External Forces", facecolor=reactioncolor, linecolor=reactioncolor.contrast)
viewer.scene.add(compression, name="Compression", facecolor=compressioncolor, linecolor=compressioncolor.contrast)
viewer.scene.add(tension, name="Tension", facecolor=tensioncolor, linecolor=tensioncolor.contrast)

viewer.show()
