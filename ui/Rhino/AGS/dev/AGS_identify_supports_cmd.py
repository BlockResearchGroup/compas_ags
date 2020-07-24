from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_identify_supports"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    vertices = form.select_vertices()
    if not vertices:
        return

    # check that the selection makes sense
    # potentially update all connected leaf edges to become "is_support"
    # or at least remove "is_load"

    # rename this attribute to "is_support"
    # is_support != is_fixed
    form.diagram.vertices_attribute('is_fixed', True, keys=vertices)

    scene.clear()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
