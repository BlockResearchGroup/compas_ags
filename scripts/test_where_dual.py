import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

FILE = compas_ags.get('debugging/zero.obj')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

form.edge_force((0, 1), +10.0)
form.edge_force((2, 3), +10.0)
form.edge_force((4, 5), +10.0)

# for edge in force.edges_where_dual({'is_external': True}):
#     dual_edge = force.dual_edge(edge)
#     print(edge, (form.halfedge[dual_edge[0]][dual_edge[1]], form.halfedge[dual_edge[1]][dual_edge[0]]))

# print(list(form.edges()))
# print(form.edge_index())
print(list(force.edges()))
# print([force.dual_edge(edge) for edge in force.edges()])
print(all(form.has_edge(force.dual_edge(edge)) for edge in force.edges()))
print(list(force.edges_where_dual({'is_ind': True})))
