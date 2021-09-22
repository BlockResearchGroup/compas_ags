import math
import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import update_diagrams_from_constraints
from compas_ags.viewers import Viewer


def view_form_force(form, force, forcescale=0.5, edge_label=False):
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

def show_constraints(form, force):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#FF0000' for key in form.vertices_where({'is_fixed_x': True})})
    viewer.draw_force(vertexcolor={key: '#FF0000' for key in force.vertices_where({'is_fixed_x': True})})
    viewer.show()

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#0000FF' for key in form.vertices_where({'is_fixed_y': True})})
    viewer.draw_force(vertexcolor={key: '#0000FF' for key in force.vertices_where({'is_fixed_y': True})})
    viewer.show()

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: str(form.edge_attribute(uv, 'target_vector')) for uv in form.edges()},
                    vertexsize=0.2,
                    # forces_on=False,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(vertexcolor={key: '#000000' for key in force.vertices_where({'is_fixed': True})},
                    edgelabel={uv: str(force.edge_attribute(uv, 'target_vector')) for uv in force.edges()})
    viewer.show()

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: str(form.edge_attribute(uv, 'target_length')) for uv in form.edges()},
                    vertexsize=0.2,
                    # forces_on=False,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(vertexcolor={key: '#000000' for key in force.vertices_where({'is_fixed': True})},
                    edgelabel={uv: str(force.edge_attribute(uv, 'target_length')) for uv in force.edges()})
    viewer.show()


# ------------------------------------------------------------------------------
#   5. Dense Constant force truss
#       - Input a non-triangulated dense truss, compute initial equilibrium
#       - Constraint top chord to constant force and move bottom chord to a sinusoidal shape
#       - Constraint the applied loads magnitude
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#   1. Get geometry, apply loads and and compute equilibrium
# ------------------------------------------------------------------------------

graph = FormGraph.from_obj(compas_ags.get('paper/exE_truss_dense.obj'))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)
force_edges = force.ordered_edges(form)

force_edge_labels1 = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels2 = {(v, u): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels = {**force_edge_labels1, **force_edge_labels2}

# prescribe force density to edge
edges_ind = [
    (17, 22),
]
load = 1.0
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', load)

index_edge = form.index_edge()

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# set the fixed corners
fixed = [14, 5]

for key in fixed:
    form.vertex_attribute(key, 'is_fixed', True)

# store lines representing the current state of equilibrium
form_lines, force_lines = store_initial_lines(form, force)

view_form_force(form, force, edge_label=True)

# --------------------------------------------------------------------------
#   3. find a different equilibrium configuration with sinus
# --------------------------------------------------------------------------

vertices_bottom_chord = [14, 19, 15, 18, 16, 17, 7, 8, 6, 9, 5]
index_edges_constant_force = [27, 25, 23, 21, 3, 0, 1, 5, 7, 9]
index_edges_constant_load = [40, 33, 39, 36, 38, 17, 19, 14, 20]

span = 5.0
x0 = 0.0
vertices_bottom_leaves = [26, 24, 27, 23, 28, 22, 29, 21, 30, 20, 31]
amplitude = 0.10

for index, key in enumerate(vertices_bottom_chord):
    x, y, _ = form.vertex_coordinates(key)
    key_leaf = vertices_bottom_leaves[index]
    _, y_leaf, _ = form.vertex_coordinates(key_leaf)
    h = amplitude*math.sin(2*math.pi*(x - x0)/span)
    form.vertex_attribute(key, 'y', y + h)
    form.vertex_attribute(key, 'is_fixed_y', True)
    form.vertex_attribute(key_leaf, 'y', y_leaf + h)

for index in edges_fix_orient:
    edge = index_edge[index]
    form.edge_attribute(edge, 'target_vector', None)

show_constraints(form, force)

# Identify auto constraints
form.identify_constraints()

# # Reflect all constraints to force diagram
force.constraints_from_dual()

show_constraints(form, force)

# fix_y_force = [8, 7, 9, 10, 11]
# for key in fix_y_force:
#     force.vertex_attribute(key, 'is_fixed_y', False)

update_diagrams_from_constraints(form, force, max_iter=100, printout=True)

view_form_force(form, force, edge_label=True)

# # more movement

for index, key in enumerate(vertices_bottom_chord):
    x, y, _ = form.vertex_coordinates(key)
    key_leaf = vertices_bottom_leaves[index]
    _, y_leaf, _ = form.vertex_coordinates(key_leaf)
    h = amplitude*math.sin(2*math.pi*(x - x0)/span)
    form.vertex_attribute(key, 'y', y + h)
    form.vertex_attribute(key, 'is_fixed_y', True)
    form.vertex_attribute(key_leaf, 'y', y_leaf + h)

update_diagrams_from_constraints(form, force, max_iter=100, printout=True)

view_form_force(form, force)

# # more movement

for index, key in enumerate(vertices_bottom_chord):
    x, y, _ = form.vertex_coordinates(key)
    key_leaf = vertices_bottom_leaves[index]
    _, y_leaf, _ = form.vertex_coordinates(key_leaf)
    h = amplitude*math.sin(2*math.pi*(x - x0)/span)
    form.vertex_attribute(key, 'y', y + h)
    form.vertex_attribute(key, 'is_fixed_y', True)
    form.vertex_attribute(key_leaf, 'y', y_leaf + h)

update_diagrams_from_constraints(form, force, max_iter=100, printout=True)

view_form_force(form, force)
