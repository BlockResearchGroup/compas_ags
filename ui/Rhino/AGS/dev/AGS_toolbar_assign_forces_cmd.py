from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import AGS_form_check_dof_cmd
import AGS_form_assign_forces_cmd
import AGS_form_update_from_qind_cmd


__commandname__ = "AGS_toolbar_assign_forces"


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

    AGS_form_assign_forces_cmd.RunCommand(True)
    # AGS_form_update_from_qind_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
