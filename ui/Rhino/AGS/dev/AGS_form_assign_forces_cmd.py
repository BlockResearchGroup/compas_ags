from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_form_assign_forces"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    # select edges and assign forces
    while True:
        edges = form.select_edges()
        if not edges:
            break
        if form.diagram.edge_attribute(edges[0], 'is_ind'):
            current = str(form.diagram.edge_attribute(edges[0], 'is_ind'))  # display T/F based on first selected
            show = compas_rhino.rs.GetString("Modify Forces on selection", defaultString=current, strings=["True", "False"])
            if show == "True":
                force_value = compas_rhino.rs.GetReal("Force on Edges (kN)", form.diagram.edge_force(edges[0]))
                for edge in edges:
                    form.diagram.edge_force(edge, force_value)
            elif show == "False":
                for edge in edges:
                    form.diagram.edge_attribute(edge, 'is_ind', False)
            else:
                pass
        else:
            force_value = compas_rhino.rs.GetReal("Force on Edges (kN)", 1.0)
            for edge in edges:
                form.diagram.edge_force(edge, force_value)
        scene.update()

    edge_index = form.diagram.edge_index()

    edges = list(form.diagram.edges_where({'is_ind': True}))

    names = [str(edge_index[edge]) for edge in edges]
    values = ["{:.3f}".format(form.diagram.edge_force(edge)) for edge in edges]
    values = compas_rhino.update_named_values(names, values)

    if values:
        for name, value in zip(names, values):
            form.diagram.edge_force(int(name), float(value))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
