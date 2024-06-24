from compas_viewer import Viewer
from compas_viewer.config import Config

import compas_ags
from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Circle
from compas.geometry import Polygon
from compas.geometry import bounding_box
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors
from compas.geometry import sum_vectors
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import FormGraph

# ==============================================================================
# Construct the graph of a Fink truss.
# ==============================================================================

graph = FormGraph.from_obj(compas_ags.get("paper/fink.obj"))

# ==============================================================================
# Identify the fixed points of the graph.
# ==============================================================================

fixed = [6, 9]

# ==============================================================================
# Assert that the graph is 2D and that it is planar.
# ==============================================================================

assert graph.is_2d(), "The graph is not 2D."
assert graph.is_planar(), "The graph is not planar."

# ==============================================================================
# Construct a planar embedding of the graph
# ==============================================================================

embedding: FormGraph = graph.copy()

if embedding.is_crossed():

    # if the graph has crossed edges
    # we create a copy without leaves
    # and compute a spring layout to find a planar embedding
    # finally we re-add the leaves towards "the outside"

    noleaves: FormGraph = embedding.copy()
    for node in embedding.leaves():
        noleaves.delete_node(node)

    assert noleaves.embed(fixed=fixed), "The graph could not be embedded in the plane using a spring layout."

    E = noleaves.number_of_edges()
    L = sum(noleaves.edge_length(edge) for edge in noleaves.edges())
    length = 0.5 * L / E

    for node in noleaves.nodes():
        embedding.node_attributes(node, "xy", noleaves.node_attributes(node, "xy"))

    for node in embedding.leaves():
        u = embedding.neighbors(node)[0]
        if u in fixed:
            continue

        a = embedding.node_attributes(u, "xyz")

        vectors = []
        for v in noleaves.neighbors(u):
            b = embedding.node_attributes(v, "xyz")
            vectors.append(normalize_vector(subtract_vectors(b, a)))

        ab = scale_vector(normalize_vector(scale_vector(sum_vectors(vectors), 1 / len(vectors))), length)
        embedding.node_attributes(node, "xyz", subtract_vectors(a, ab))

# ==============================================================================
# Construct a form diagram of the embedding
# ==============================================================================

form = FormDiagram.from_graph(embedding)

# ==============================================================================
# Visualize the result
# ==============================================================================

loadcolor = Color.green().darkened(50)
reactioncolor = Color.green().darkened(50)
tensioncolor = Color.red().lightened(25)
compressioncolor = Color.blue().lightened(25)

config = Config()
config.renderer.view = "top"
config.renderer.gridsize = [100, 100, 100, 100]

viewer = Viewer(config=config)

viewer.scene.add(form, show_faces=False, show_lines=True, linewidth=2, name="FormDiagram")

circles = [Circle.from_point_and_radius(form.vertex_point(vertex) + [0, 0, 0.001], 0.1).to_polygon(n=128) for vertex in form.vertices()]
viewer.scene.add(circles, name="Vertices", facecolor=Color.white(), linecolor=Color.black())

viewer.show()
