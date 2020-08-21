from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from compas.geometry import subtract_vectors
from compas.geometry import add_vectors


__commandname__ = "AGS_form_location"


def RunCommand(is_interactive):
    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    if not form:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    start = compas_rhino.pick_point('Pick a point to move from.')
    if start:
        end = compas_rhino.pick_point('Pick a point to move to.')
        if end:
            vector = subtract_vectors(end, start)
            xyz = form.artist.anchor_point
            new_xyz = add_vectors(xyz, vector)
            form.artist.anchor_point = new_xyz

    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
