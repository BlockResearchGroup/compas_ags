from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_force_select_anchor"


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

    vertex_xyz = force.artist.vertex_xyz

    vertex = force.select_vertex("Select the anchor vertex.")
    if vertex is None:
        return

    force.anchor = vertex
    force.location = vertex_xyz[vertex]

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
