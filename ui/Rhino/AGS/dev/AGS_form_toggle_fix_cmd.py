from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_form_toggle_fix"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    if not form:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    # select fixed vertices
    while True:
        vertices = form.select_vertices()
        if not vertices:
            break
        for vertex in vertices:
            form.diagram.vertex_attribute(vertex, 'is_fixed', not form.diagram.vertex_attribute(vertex, 'is_fixed'))

        scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
