
from compas_ags.viewers import Viewer
from compas_ags.ags import form_update_from_force
from compas_ags.ags import force_update_from_constraints

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
                    edgelabel={uv: form.edge_attribute(uv, 'target_length') for uv in form.edges()},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(vertexcolor={key: '#000000' for key in force.vertices_where({'is_fixed': True})},
                    edgelabel={uv: force.edge_attribute(uv, 'target_length') for uv in force.edges()})
    viewer.show()

def view_with_initial_stage(form, force):
    viewer = Viewer(form, force, delay_setup=False)

    viewer.draw_form(lines=form_lines,
                    forces_on=True,
                    vertexlabel={key: key for key in form.vertices()},
                    external_on=True,
                    vertexsize=0.2,
                    edgelabel={uv: index for index, uv in enumerate(form.edges())}
                    )

    viewer.draw_force(lines=force_lines,
                    vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel=force_edge_labels
                    )

    viewer.show()

def view_with_force_lengths(form, force):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={(u, v): round(form.edge_length(u, v), 3) for u, v in form.edges()},
                    vertexsize=0.2,
                    forces_on=True)
    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel={(u, v): round(force.edge_length(u, v), 3) for u, v in force.edges()})
    viewer.show()

def view_form_force(form, force):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=True)
    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel=force_edge_labels)
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

def view_form_force2(form, force, forcescale=0.5, edge_label=True, qid=True):
    if edge_label:
        form_edge_label = {uv: index for index, uv in enumerate(form.edges())}
        force_edge_label = force_edge_labels
    else:
        form_edge_label = None
        force_edge_label = None


    viewer = Viewer(form, force, delay_setup=False)
    if not qid:
        viewer.default_independent_edge_color = '#00ff00'
    viewer.draw_form(edgelabel= form_edge_label,
                    forces_on=True,
                    forcescale=forcescale,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(edgelabel=force_edge_label)
    viewer.show()

def view_with_initial_stage2(form, force, forcescale=0.5, edge_label=True, qid=True):
    if edge_label:
        form_edge_label = {uv: index for index, uv in enumerate(form.edges())}
        force_edge_label = force_edge_labels
    else:
        form_edge_label = None
        force_edge_label = None

    viewer = Viewer(form, force, delay_setup=False)
    if not qid:
        viewer.default_independent_edge_color = '#00ff00'
    viewer.draw_form(lines=form_lines,
                    forces_on=True,
                    external_on=True,
                    forcescale=forcescale,
                    edgelabel= form_edge_label,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(lines=force_lines,
                    edgelabel=force_edge_label
                    )
    viewer.show()


# ------------------------------------------------------------------------------
#   1. Get geometry, apply loads and and compute equilibrium
# ------------------------------------------------------------------------------

import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form

graph = FormGraph.from_obj(compas_ags.get('paper/ex3_truss.obj'))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)
force_edges = force.ordered_edges(form)

force_edge_labels1 = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels2 = {(v, u): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels = {**force_edge_labels1, **force_edge_labels2}

# View centroidal dual
# view_form_force(form, force)

# ------------------------------------------------------------------------------
#   2. prescribe edge force density and set fixed vertices
# ------------------------------------------------------------------------------
# prescribe force density to edge
edges_ind = [
    (13, 14),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', +2.)

index_edge = form.index_edge()

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# set the fixed corners
fixed = [5, 1]

for key in fixed:
    form.vertex_attribute(key, 'is_fixed', True)
    # form.vertex_attribute(key, 'is_fixed_y', True)

# store lines representing the current state of equilibrium
form_lines, force_lines = store_initial_lines(form, force)


view_form_force2(form, force, forcescale=1.0, edge_label=False, qid=False)
# view_form_force(form, force)
view_with_force_lengths(form, force)

# ------------------------------------------------------------------------------
#   3. prescribe constraints on the form and update form and force
# ------------------------------------------------------------------------------

from compas_ags.ags import update_diagrams_from_constraints

# A. Fix orientation of edges at bottom chord
edges_fix_orient = [13, 19, 17, 15, 4]

for index in edges_fix_orient:
    edge = index_edge[index]
    sp, ep = form.edge_coordinates(*edge)
    dx = ep[0] - sp[0]
    dy = ep[1] - sp[1]
    length = (dx**2 + dy**2)**0.5
    form.edge_attribute(edge, 'target_vector', [dx/length, dy/length])
    # see if the target vector should also apply to the force diagram

# A1. Fix the nodes on the bottom to Y... Should be not necessary, but it has to be applied in the other direction...

vertices_bottom_chord = [13, 11, 9, 7]

for key in vertices_bottom_chord:
    form.vertex_attribute(key, 'is_fixed_y', True)

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

show_constraints(form, force)

update_diagrams_from_constraints(form, force, max_iter=100)

view_with_initial_stage2(form, force, forcescale=1.0, edge_label=False, qid=False)
# view_form_force(form, force)
view_with_force_lengths(form, force)
# view_with_initial_stage2(form, force, forcescale=1.0)
# view_with_initial_stage2(form, force, forcescale=1.0, edge_label=False)

# # ------------------------------------------------------------------------------
# #   3. delta support problem
# # ------------------------------------------------------------------------------

# # delta_support = 1.0
# # support_move = [1, 6]

# # for key in support_move:
# #     _, y, _ = form.vertex_coordinates(key)
# #     form.vertex_attribute(key, 'y', y + delta_support)

# # # A. Release orientation of edges at bottom chord
# # edges_fix_orient = [13, 19, 17, 15, 4]

# # for index in edges_fix_orient:
# #     form.edge_attribute(index_edge[index], 'has_fixed_orientation', False)

# # # Identify auto constraints
# # form.identify_constraints()

# # # # Reflect all constraints to force diagram
# # force.constraints_from_dual()

# # fix_y_force = [8, 7, 9, 10, 11]
# # for key in fix_y_force:
# #     force.vertex_attribute(key, 'is_fixed_y', False)

# # show_constraints(form, force)

# # # update_diagrams_from_constraints(form, force, callback=view_with_initial_stage, max_iter=100, printout=True)
# # update_diagrams_from_constraints(form, force, max_iter=500, printout=True)

# # view_form_force(form, force)
# # view_with_initial_stage(form, force)

# # --------------------------------------------------------------------------
# #   4. find a different equilibrium configuration with sinus
# # --------------------------------------------------------------------------

# import math

# span = 5.0
# x0 = 0.0
# vertices_bottom_chord = [5, 13, 11, 9, 7, 1]
# vertices_bottom_leaves = [15, 14, 12, 10, 8, 6]
# amplitude = 0.15

# for index, key in enumerate(vertices_bottom_chord):
#     x, y, _ = form.vertex_coordinates(key)
#     key_leaf = vertices_bottom_leaves[index]
#     _, y_leaf, _ = form.vertex_coordinates(key_leaf)
#     h = amplitude*math.sin(2*math.pi*(x - x0)/span)
#     form.vertex_attribute(key, 'y', y + h)
#     form.vertex_attribute(key, 'is_fixed_y', True)
#     form.vertex_attribute(key_leaf, 'y', y_leaf + h)

# # Identify auto constraints
# form.identify_constraints()

# # # Reflect all constraints to force diagram
# force.constraints_from_dual()

# fix_y_force = [8, 7, 9, 10, 11]
# for key in fix_y_force:
#     force.vertex_attribute(key, 'is_fixed_y', False)

# # show_constraints(form, force)
# # view_with_initial_stage(form, force)

# # update_diagrams_from_constraints(form, force, callback=view_with_initial_stage, max_iter=100, printout=True)
# update_diagrams_from_constraints(form, force, max_iter=500, printout=True)

# view_form_force2(form, force, forcescale=1.0, edge_label=False)
# view_form_force(form, force)
# view_with_initial_stage(form, force)

# # more movement

# for index, key in enumerate(vertices_bottom_chord):
#     x, y, _ = form.vertex_coordinates(key)
#     key_leaf = vertices_bottom_leaves[index]
#     _, y_leaf, _ = form.vertex_coordinates(key_leaf)
#     h = amplitude*math.sin(2*math.pi*(x - x0)/span)
#     form.vertex_attribute(key, 'y', y + h)
#     form.vertex_attribute(key, 'is_fixed_y', True)
#     form.vertex_attribute(key_leaf, 'y', y_leaf + h)

# view_with_initial_stage(form, force)

# update_diagrams_from_constraints(form, force, max_iter=500, printout=True)

# view_form_force(form, force)
# view_with_initial_stage(form, force)
