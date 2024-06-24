import compas_ags
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

embedding = graph.copy()

if embedding.is_crossed():

    # if the graph has crossed edges
    # we create a copy without leaves
    # and compute a spring layout to find a planar embedding
    # finally we re-add the leaves towards "the outside"

    noleaves = embedding.copy()
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

# plotter = MeshPlotter(form, figsize=(12, 7.5))
# plotter.draw_vertices(text="key", radius=0.3)
# plotter.draw_edges()
# plotter.show()
