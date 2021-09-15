import compas_ags
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import form_update_from_force
from compas_ags.viewers import Viewer


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
#   2. Dragging the force diagram and updating form diagram
#       - Find a deeper form diagram
#       - Invert compression/tension
# ------------------------------------------------------------------------------

input_file = compas_ags.get('paper/exB_arch-output.obj')

form = FormDiagram.from_json(input_file)
force = ForceDiagram.from_formdiagram(form)

# create label for plots
force_edges = force.ordered_edges(form)
force_edge_labels = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels.update({(v, u): index for index, (u, v) in enumerate(force_edges)})

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# visualise initial solution
view_form_force(form, force, forcescale=2.0)

# Identify auto constraints
form.identify_constraints()

form_lines, force_lines = store_initial_lines(form, force)

# ---------------------------------------------
# Move to change sag (deeper form diagram)

move_vertices = [0, 9, 8]
translation = +1.81
for key in move_vertices:
    x0 = force.vertex_attribute(key, 'x')
    force.vertex_attribute(key, 'x', x0 + translation)

form_update_from_force(form, force)

view_with_initial_stage(form, force, forcescale=2.0, edge_label=False)

# ---------------------------------------------
# Move to invert compression to tension

move_vertices = [0, 9, 8]
translation = +4.00
for key in move_vertices:
    x0 = force.vertex_attribute(key, 'x')
    force.vertex_attribute(key, 'x', x0 + translation)

form_update_from_force(form, force)

view_with_initial_stage(form, force, forcescale=2.0, edge_label=False)
