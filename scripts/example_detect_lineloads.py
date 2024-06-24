import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.viewers import Viewer
from compas_ags.ags import form_update_from_force
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import ConstraintsCollection
from compas_ags.ags import form_update_from_force

# ------------------------------------------------------------------------------
#   1. create a simple arch from nodes and edges, make form and force diagrams
# ------------------------------------------------------------------------------

graph = FormGraph.from_json(compas_ags.get("paper/gs_arch.json"))
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
#   2. prescribe edge force density and set fixed vertices
# ------------------------------------------------------------------------------
# prescribe force density to edge
edges_ind = [
    (2, 11),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), "is_ind", True)
    form.edge_attribute((u, v), "q", -1.0)

# set the fixed corners
left = 2
right = 9
fixed = [left, right]

for key in fixed:
    form.vertex_attribute(key, "is_fixed", True)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# store lines representing the current state of equilibrium
form_lines = []
for u, v in form.edges():
    form_lines.append({"start": form.vertex_coordinates(u, "xy"), "end": form.vertex_coordinates(v, "xy"), "width": 1.0, "color": "#cccccc", "style": "--"})

force_lines = []
for u, v in force.edges():
    force_lines.append({"start": force.vertex_coordinates(u, "xy"), "end": force.vertex_coordinates(v, "xy"), "width": 1.0, "color": "#cccccc", "style": "--"})

# Detect the leaves of form diagram:

form.identify_constraints()

# Next
# Reflect the leaves cosntraints in the force diagram:

# edge_index = form.edge_index()
# # index = edge_index[edge_form]
# edges_force = list(force.ordered_edges(form))
# vertex_leaves= form.leaves()

# for edge in form.leaf_edges():
#     index = edge_index[edge]
#     dual = edges_force[index]
#     sp, ep = form.edge_coordinates(edge)
#     print('INDEX -->', index)
#     print('original edge -->', edge)
#     print('dual edge -->', dual)

force_edge_labels1 = {(u, v): index for index, (u, v) in enumerate(force.ordered_edges(form))}
force_edge_labels2 = {(v, u): index for index, (u, v) in enumerate(force.ordered_edges(form))}
force_edge_labels = {**force_edge_labels1, **force_edge_labels2}

# --------------------------------------------------------------------------
#   3. force diagram manipulation and modify the form diagram
# --------------------------------------------------------------------------

# modify the geometry of the force diagram moving nodes further at right to the left
move_vertices = [0, 9, 8]
translation = +1.0
for key in move_vertices:
    x0 = force.vertex_attribute(key, "x")
    force.vertex_attribute(key, "x", x0 + translation)

form_update_from_force(form, force)

# ------------------------------------------------------------------------------
#   4. display the orginal configuration
#      and the configuration after modifying the force diagram
# ------------------------------------------------------------------------------
viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(
    lines=form_lines,
    forces_on=True,
    vertexlabel={key: key for key in form.vertices()},
    external_on=False,
    vertexsize=0.2,
    vertexcolor={**{key: "#000000" for key in form.fixed()}, **{key: "#FF0000" for key in form.fixed_x()}},
    edgelabel={uv: index for index, uv in enumerate(form.edges())},
)

viewer.draw_force(lines=force_lines, vertexlabel={key: key for key in force.vertices()}, vertexsize=0.2, edgelabel=force_edge_labels)

viewer.show()
