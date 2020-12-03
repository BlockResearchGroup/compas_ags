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

    form.diagram.vertices_attribute('is_fixed', False)
    scene.update()

    vertices = form.select_vertices("Fix selected vertices (unfix all others)")
    if not vertices:
        return

    form.diagram.vertices_attribute('is_fixed', True, keys=vertices)
    scene.update()

    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
