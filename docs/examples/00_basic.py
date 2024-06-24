from compas_viewer import Viewer
from compas_viewer.config import Config

import compas_ags
from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Circle
from compas.geometry import Polygon
from compas.geometry import bounding_box
from compas_ags.ags import graphstatics
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import FormGraph

# ------------------------------------------------------------------------------
# 1. get lines of a plane triangle frame in equilibrium, its applied loads and reaction forces
#    make form and force diagrams
# ------------------------------------------------------------------------------

graph = FormGraph.from_obj(compas_ags.get("paper/gs_form_force.obj"))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
# 2. set applied load
# ------------------------------------------------------------------------------

# choose an independent edge and set the magnitude of the applied load
# the system is statically determinate, thus choosing one edge is enough
form.edge_force(0, -30.0)

# update force densities of form and force diagrams
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# ------------------------------------------------------------------------------
# 3. display force and form diagrams
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
