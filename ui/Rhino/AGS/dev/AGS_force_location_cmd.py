from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

# from compas.geometry import subtract_vectors
# from compas.geometry import add_vectors


__commandname__ = "AGS_force_location"


def RunCommand(is_interactive):
    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    force = scene.find_by_name('Force')[0]

    if not force:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return

    anchor_vertex = force.select_vertex('Select the anchor vertex.')
    if anchor_vertex:
        force.anchor_vertex = anchor_vertex

    if force.move():
        scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
