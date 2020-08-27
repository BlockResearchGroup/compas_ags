from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_form_select_fixed"


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
            vertices = form.select_vertices("Fix selected vertices (unfix all others).")
            if vertices:
                form.diagram.vertices_attribute('is_fixed', False)
                form.diagram.vertices_attribute('is_fixed', True, keys=vertices)
                scene.update()
            else:
                return

        elif option == "Toggle":
            vertices = form.select_vertices("Toggle the fixed state of selected vertices.")
            if vertices:
                for vertex in vertices:
                    form.diagram.vertex_attribute(vertex, 'is_fixed', not form.diagram.vertex_attribute(vertex, 'is_fixed'))
                scene.update()
            else:
                return

        else:
            raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
