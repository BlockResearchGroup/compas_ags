from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_form_select_ind"


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

    options = ["Select", "Toggle"]
    while True:
        option = compas_rhino.rs.GetString("Identification Mode", options[0], options)
        if not option or option not in options:
            return

        if option == "Select":
            edges = form.select_edges("Mark selected edges as independent (all others as dependent).")
            if edges:
                form.diagram.edges_attribute('is_ind', False)
                form.diagram.edges_attribute('is_ind', True, keys=edges)
                scene.update()

        elif option == "Toggle":
            edges = form.select_edges("Toggle the independent state of selected edges.")
            if edges:
                for edge in edges:
                    form.diagram.edge_attribute(edge, 'is_ind', not form.diagram.edge_attribute(edge, 'is_ind'))
                scene.update()

        else:
            raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
