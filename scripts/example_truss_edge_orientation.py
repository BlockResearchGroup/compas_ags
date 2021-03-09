import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.viewers import Viewer
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import form_update_from_force
from compas_ags.ags import force_update_from_constraints

# ------------------------------------------------------------------------------
#   1. Get OBJ file for the geometry
# ------------------------------------------------------------------------------

graph = FormGraph.from_obj(compas_ags.get('paper/gs_truss.obj'))

# Add horizontal line to graph to make Structure isostatic.
lines = graph.to_lines()
lines.append(([-2.0, 0.0, 0.0], [0.0, 0.0, 0.0]))
graph = FormGraph.from_lines(lines)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
#   2. prescribe edge force density and set fixed vertices
# ------------------------------------------------------------------------------
# prescribe force density to edge
edges_ind = [
    (8, 9),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', +1.)

index_edge = form.index_edge()

# set the fixed corners
left = 6
right = 1
fixed = [left, right]

for key in fixed:
    form.vertex_attribute(key, 'is_fixed', True)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# store lines representing the current state of equilibrium
form_lines = []
for u, v in form.edges():
    form_lines.append({
        'start': form.vertex_coordinates(u, 'xy'),
        'end': form.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

force_lines = []
for u, v in force.edges():
    force_lines.append({
        'start': force.vertex_coordinates(u, 'xy'),
        'end': force.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

force_edges = force.ordered_edges(form)

force_edge_labels1 = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels2 = {(v, u): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels = {**force_edge_labels1, **force_edge_labels2}

# ------------------------------------------------------------------------------
#   3. prescribe constraints on the form
# ------------------------------------------------------------------------------

# # A. Fix orientation of edges at bottom chord
edges_fix_orient = [13, 14, 16, 18, 4]

for index in edges_fix_orient:
    form.edge_attribute(index_edge[index], 'has_fixed_orientation', True)

# B. Assign forces on the top chord to have the same length
index_edges_constant_force = [0, 1, 5, 7, 9]
L = force.edge_length(*force.ordered_edges(form)[1])

for index in index_edges_constant_force:
    form.edge_attribute(index_edge[index], 'target_length', L)

# C. Make edge 4 short (less force)  - Try options B and C...
# edges_change = [4, 13]
# new_length = 5.5
# for edge_change in edges_change:
#     form.edge_attribute(index_edge[edge_change], 'target_length', new_length)

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(edgelabel={uv: index for index, uv in enumerate(form.edges())})
viewer.draw_force(edgelabel=force_edge_labels)
viewer.show()

# --------------------------------------------------------------------------
#   4. find force diagram to respect force/geometry constraints and update equilibtium
# --------------------------------------------------------------------------

# Identify auto constraints
form.identify_constraints()

# Reflect all constraints to force diagram
force.constraints_from_dual()

# Update force diagram given constraints
force_update_from_constraints(force)

# Update form diagram based on force diagram
form_update_from_force(form, force)

# ------------------------------------------------------------------------------
#   5. display the orginal configuration
#      and the configuration after modifying the force diagram
# ------------------------------------------------------------------------------
viewer = Viewer(form, force, delay_setup=False)

lengths_uv = {}
for u, v in force.edges():
    lengths_uv[(u, v)] = force.edge_length(u, v)

viewer.draw_form(lines=form_lines,
                 forces_on=True,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=False,
                 vertexsize=0.2,
                 vertexcolor={key: '#000000' for key in fixed},
                 )

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel=lengths_uv
                  )

viewer.show()
