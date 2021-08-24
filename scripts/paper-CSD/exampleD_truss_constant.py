import compas_ags
from compas_ags.viewers import Viewer
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import update_diagrams_from_constraints


def view_form_force(form, force, forcescale=0.5, edge_label=True):
    if edge_label:
        form_edge_label = {uv: index for index, uv in enumerate(form.edges())}
        force_edge_label = force_edge_labels
    else:
        form_edge_label = None
        force_edge_label = None

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(edgelabel=form_edge_label,
                     forces_on=True,
                     forcescale=forcescale,
                     vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(edgelabel=force_edge_label)
    viewer.show()


def view_with_initial_stage(form, force, forcescale=0.5, edge_label=True):
    if edge_label:
        form_edge_label = {uv: index for index, uv in enumerate(form.edges())}
        force_edge_label = force_edge_labels
    else:
        form_edge_label = None
        force_edge_label = None

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(lines=form_lines,
                     forces_on=True,
                     external_on=True,
                     forcescale=forcescale,
                     edgelabel=form_edge_label,
                     vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(lines=force_lines,
                      edgelabel=force_edge_label
                      )
    viewer.show()


def store_initial_lines(form, force):

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

    return form_lines, force_lines


# ------------------------------------------------------------------------------
#   4. Constant force truss
#       - Input a non-triangulated truss, compute initial equilibrium
#       - Move the form diagram support
#       - Move one of the internal nodes to a specific position
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#   1. Get geometry, apply loads and and compute equilibrium
# ------------------------------------------------------------------------------

input_file = compas_ags.get('paper/exD_truss.obj')

graph = FormGraph.from_obj(input_file)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)
force_edges = force.ordered_edges(form)

force_edge_labels1 = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels2 = {(v, u): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels = {**force_edge_labels1, **force_edge_labels2}

# prescribe force density to edge
edges_ind = [
    (13, 14),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', +2.)

index_edge = form.index_edge()

# set the fixed corners
fixed = [5, 1]

for key in fixed:
    form.vertex_attribute(key, 'is_fixed', True)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# store lines representing the current state of equilibrium
form_lines, force_lines = store_initial_lines(form, force)

view_form_force(form, force, forcescale=1.0, edge_label=False)

# ------------------------------------------------------------------------------
#   2. prescribe constraints on the form and update form and force
# ------------------------------------------------------------------------------

# A. Fix orientation of edges at bottom chord
edges_fix_orient = [13, 19, 17, 15, 4]

for index in edges_fix_orient:
    edge = index_edge[index]
    sp, ep = form.edge_coordinates(*edge)
    dx = ep[0] - sp[0]
    dy = ep[1] - sp[1]
    length = (dx**2 + dy**2)**0.5
    form.edge_attribute(edge, 'target_vector', [dx/length, dy/length])

# B. Assign forces on the top chord to have the same length
index_edges_constant_force = [9, 7, 5, 0, 1]
L = 5.0

for index in index_edges_constant_force:
    form.edge_attribute(index_edge[index], 'target_length', L)

# C. Guarantee constant force application
index_edges_constant_load = [20, 18, 16, 14]
load = 2.0

for index in index_edges_constant_load:
    form.edge_attribute(index_edge[index], 'target_length', load)

# Identify auto constraints
form.identify_constraints()

# Reflect all constraints to force diagram
force.constraints_from_dual()

update_diagrams_from_constraints(form, force)

view_with_initial_stage(form, force, forcescale=1.0, edge_label=False)
