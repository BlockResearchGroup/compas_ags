from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_force_scale"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    force = objects[0]

    # vertex = force.select_vertex(message="Pick base node.")
    # if vertex:
    #     force.artist.anchor_point = force.artist.vertex_xyz[vertex]
    #     force.artist.anchor_vertex = vertex

    scale_factor = compas_rhino.rs.GetReal("Scale factor", force.artist.scale)
    force.artist.scale = scale_factor

    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
