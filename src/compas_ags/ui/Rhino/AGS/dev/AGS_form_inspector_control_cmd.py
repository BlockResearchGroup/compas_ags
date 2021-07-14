from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import AGS_form_inspector_on_cmd
import AGS_form_inspector_off_cmd

__commandname__ = "AGS_form_inspector_control"


def RunCommand(is_interactive):
    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    answer = compas_rhino.rs.GetString("Force Polygons Inspector", "Cancel", ["On", "Off", "Cancel"])
    if answer == "On":
        AGS_form_inspector_on_cmd.RunCommand(True)
    if answer == "Off":
        AGS_form_inspector_off_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
