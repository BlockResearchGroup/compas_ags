
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


def view_with_initial_stage(form, force, forcescale=0.5):
    viewer = Viewer(form, force, delay_setup=False)

    viewer.draw_form(lines=form_lines,
                    forces_on=True,
                    vertexlabel={key: key for key in form.vertices()},
                    external_on=True,
                    vertexsize=0.2,
                    forcescale=forcescale,
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

def view_form_force(form, force, forcescale=0.5):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=True,
                    forcescale=forcescale,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel=force_edge_labels)
    viewer.show()

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
#   0. Problem of getting to a funicular shape
#       - Input a circular arch
#       - Input "target forces" for the loads applied
#       - Specify the reaction magnitudes, such that the vertical eq. is fulfilled
#       - No vertex constraints apply on the force diag. (only to the ind. edge)
# ------------------------------------------------------------------------------

import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import update_diagrams_from_constraints
from compas_ags.viewers import Viewer


graph = FormGraph.from_obj(compas_ags.get('paper/exA_tree.obj'))
form = FormDiagram.from_graph(graph)
edge_index = form.edge_index()
index_edge = form.index_edge()
# key_index = form.key_index()

# create a dual force diagram
force = ForceDiagram.from_formdiagram(form)

# create label for plots
force_edges = force.ordered_edges(form)
force_edge_labels = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels.update({(v, u): index for index, (u, v) in enumerate(force_edges)})

view_form_force(form, force, forcescale=2.0)

supports = [1]
for key in supports:
    form.vertex_attribute(key, 'is_fixed', True)

view_form_force(form, force, forcescale=2.0)

# Identify auto constraints
form.identify_constraints()

# for uv in form.edges_where({'is_load': True}):
#     print('is_load ->', edge_index[uv], uv)
# for uv in form.edges_where({'is_reaction': True}):
#     print('is_reaction ->', edge_index[uv], uv)

fd_applied = -1.0
ind_edge = (8, 10)  # works 24 iterations
# ind_edge = (7, 8)  # works 19 iterations
form.edge_attribute(ind_edge, 'is_ind', True)
form.edge_attribute(ind_edge, 'q', fd_applied)

form.vertex_attribute(7, 'is_fixed_y', True)

# view the centroidal dual
# view_form_force(form, force)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# visualise initial solution
view_form_force(form, force, forcescale=2.0)
view_with_force_lengths(form, force)

# store lines for cool plot
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

# set target lengths
for u, v in form.edges_where({'is_load': True}):
    form.edge_attribute((u, v), 'target_length', abs(fd_applied))

# # set reaction symmetry
# react_y = [4, 15]
# for index in react_y:
#     form.edge_attribute(index_edge[index], 'target_length', 3.0)

# Reflect all constraints to force diagram
force.constraints_from_dual()

# release x:
# release_x = [1, 2, 3, 4, 5, 6, 7]
# for key in force.vertices():
#     force.vertex_attribute(key, 'is_fixed_y', False)

show_constraints(form, force)

# update_diagrams_from_constraints(form, force, callback=None, printout=False, max_iter=100)
update_diagrams_from_constraints(form, force, callback=view_with_force_lengths, printout=True, max_iter=20)

view_form_force(form, force, forcescale=2.0)
view_with_initial_stage(form, force, forcescale=2.0)
view_with_force_lengths(form, force)

# form.to_json(compas_ags.get('paper/ex0_arch-output.obj'))