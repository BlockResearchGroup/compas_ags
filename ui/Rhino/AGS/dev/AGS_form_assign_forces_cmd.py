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

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    form = objects[0]

    options = ["Select", "Toggle", "Skip"]
    
    while True:
        option = compas_rhino.rs.GetString("Identification Mode", options[0], options)
        if not option or option not in options:
            return

        if option == "Skip":
            break

        elif option == "Select":
            edges = form.select_edges("Select the independent edges.")
            if edges:
                form.diagram.edges_attribute('is_ind', False)
                form.diagram.edges_attribute('is_ind', True, keys=edges)
                scene.update()
            else:
                break

        elif option == "Toggle":
            edges = form.select_edges("Toggle the independent state of selected edges.")
            if edges:
                for edge in edges:
                    form.diagram.edge_attribute(edge, 'is_ind', not form.diagram.edge_attribute(edge, 'is_ind'))
                scene.update()
            else:
                break

        else:
            raise NotImplementedError

    # update the force values of the independent edges

    edges = list(form.diagram.edges_where({'is_ind': True}))

    if not len(edges):
        compas_rhino.display_message("""
None of the edges of the diagram are marked as "independent".
Forces can only be assigned to "independent" edges.
Please select the independent edges first.""")
        return

    edge_index = form.diagram.edge_index()

    names = [edge_index[edge] for edge in edges]

    values = [form.diagram.edge_attribute(edge, 'f') for edge in edges]
    values = compas_rhino.update_named_values(names, values, message='Independent edges.', title='Update force values.')
    if values:
        for edge, value in zip(edges, values):
            try:
                F = float(value)
            except (ValueError, TypeError):
                pass
            else:
                L = form.diagram.edge_length(*edge)
                Q = F / L
                form.diagram.edge_attribute(edge, 'f', F)
                form.diagram.edge_attribute(edge, 'q', Q)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
