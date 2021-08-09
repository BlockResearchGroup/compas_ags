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
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
#   1. Dragging nodes of form and force diagram
#       - Input a parabolic arch (uniform load case).
#       - Drag nodes to increase sag - drag nodes to invert to tension.
#       - Drag nodes of
#       - No vertex constraints apply on the force diag. (only to the ind. edge)
# ------------------------------------------------------------------------------

import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import update_diagrams_from_constraints
from compas_ags.ags import form_update_from_force
from compas_ags.viewers import Viewer

input_file = compas_ags.get('paper/ex0_arch-output.obj')

form = FormDiagram.from_json(input_file)
force = ForceDiagram.from_formdiagram(form)
index_edge = form.index_edge()

# create label for plots
force_edges = force.ordered_edges(form)
force_edge_labels = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels.update({(v, u): index for index, (u, v) in enumerate(force_edges)})

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# visualise initial solution
view_form_force(form, force, forcescale=2.0)
view_with_force_lengths(form, force)

form_lines, force_lines = store_initial_lines(form, force)

# ---------------------------------------------
########## Add constraints on force of edge #2

edges_constant_force = [2]
L = 6.0
# L = 4.5
# L = 4.4  # works
# L = 4.3  # does not work
for index in edges_constant_force:
    form.edge_attribute(index_edge[index], 'target_length', L)

# # do this:
# edges_constant_force = [15, 4]
# L = 3.0
# for index in edges_constant_force:
#     form.edge_attribute(index_edge[index], 'target_length', L)

# Reflect all constraints to force diagram
force.constraints_from_dual()

# release x, or fix y
release_x = [1, 2, 3, 4, 5, 6, 7]
for key in release_x:
    force.vertex_attribute(key, 'is_fixed_x', False)

show_constraints(form, force)

# update_diagrams_from_constraints(form, force, max_iter=200, callback=view_with_initial_stage, printout=True)
update_diagrams_from_constraints(form, force, max_iter=200, callback=None, printout=True)

view_with_initial_stage(form, force)
view_with_force_lengths(form, force)



