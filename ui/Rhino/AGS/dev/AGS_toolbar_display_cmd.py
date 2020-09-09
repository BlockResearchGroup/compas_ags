from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import AGS_form_move_cmd
import AGS_form_displaysettings_cmd
import AGS_force_move_cmd
import AGS_force_select_anchor_cmd
import AGS_force_scale_cmd
import AGS_force_displaysettings_cmd


__commandname__ = "AGS_toolbar_display"
"""ATTENTION!
This cmd will be deleted (replaced by toolbar_force_display_cmd, toolbar_form_display_cmd...)
"""


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    if not scene:
        return

    if not scene.find_by_name('Form'):
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    if not scene.find_by_name('Force'):
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return

    options = ["FormLocation", "FormDisplay", "ForceLocation", "ForceAnchor", "ForceScale", "ForceDisplay"]
    option = compas_rhino.rs.GetString("Display:", strings=options)

    if not option:
        return

    if option == "FormLocation":
        AGS_form_move_cmd.RunCommand(True)

    elif option == "FormDisplay":
        AGS_form_displaysettings_cmd.RunCommand(True)

    elif option == "ForceLocation":
        AGS_force_move_cmd.RunCommand(True)

    elif option == "ForceAnchor":
        AGS_force_select_anchor_cmd.RunCommand(True)

    elif option == "ForceScale":
        AGS_force_scale_cmd.RunCommand(True)

    elif option == "ForceDisplay":
        AGS_force_displaysettings_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
