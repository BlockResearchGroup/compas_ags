from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino

from compas_ags.rhino import AttributesForm


__commandname__ = "AGS_edges_table"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    form = scene.find_by_name("Form")[0]

    objects = scene.find_by_name("Force")
    if objects:
        force = objects[0]
    else:
        force = None

    # Turn on edge labels
    original_setting = form.settings["show.edgelabels"]
    form.settings["show.edgelabels"] = True
    scene.update()

    AttributesForm.from_sceneNode(form, dual=force)

    # Revert to original setting
    form.settings["show.edgelabels"] = original_setting
    scene.update()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
