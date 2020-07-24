from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_force_anchor"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    force = scene.find_by_name('Force')[0]

    vertex = force.select_vertex()
    if vertex is not None:
        force.artist.anchor_vertex = vertex

        point = compas_rhino.pick_point()
        if point:
            force.artist.anchor_point = point

    scene.clear()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
