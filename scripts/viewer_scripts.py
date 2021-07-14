# Sniplets syle
from compas_ags.viewers import Viewer

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
                    edgelabel={(u, v): form.edge_length(u, v) for u, v in form.edges()},
                    vertexsize=0.2,
                    forces_on=True)
    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel={(u, v): force.edge_length(u, v) for u, v in force.edges()})
    viewer.show()

def view_with_edge_attribute(form, force, attr):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={(u, v): str(form.edge_attribute((u, v), attr)) for u, v in form.edges()},
                    vertexsize=0.2,
                    forces_on=True)
    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel={(u, v): str(form.edge_attribute((u, v), attr)) for u, v in form.edges()})
    viewer.show()

def view_reactions_and_loads(form, force):
    edgecolor_reaction = {(u, v): '#FF0000' for u, v in form.edges_where({'is_reaction': True})}
    edgecolor_load = {(u, v): '#0000FF' for u, v in form.edges_where({'is_load': True})}
    edge_color_form = {**edgecolor_reaction, **edgecolor_load}

    dual_edgecolor_reaction = {(u, v): '#FF0000' for u, v in force.edges_where_dual({'is_reaction': True})}
    dual_edgecolor_reaction = {(u, v): '#0000FF' for u, v in force.edges_where_dual({'is_load': True})}
    edge_color_force = {**dual_edgecolor_reaction, **dual_edgecolor_reaction}

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    external_on=False,
                    forces_on=False,
                    edgecolor=edge_color_form,
                    edgelabel={uv: index for index, uv in enumerate(form.edges())})
    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel=force_edge_labels,
                    edgecolor=edge_color_force)

    viewer.show()

def show_constraints(form, force):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#FF0000' for key in form.vertices_where({'is_fixed_x': True})})
    viewer.draw_force(edgelabel=force_edge_labels,
                    vertexcolor={key: '#FF0000' for key in force.vertices_where({'is_fixed_x': True})})
    viewer.show()
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#0000FF' for key in form.vertices_where({'is_fixed_y': True})})
    viewer.draw_force(edgelabel=force_edge_labels,
                    vertexcolor={key: '#0000FF' for key in force.vertices_where({'is_fixed_y': True})})
    viewer.show()
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#000000' for key in form.fixed()})
    viewer.draw_force(edgelabel=force_edge_labels,
                    vertexcolor={key: '#000000' for key in force.fixed()})
    viewer.show()
