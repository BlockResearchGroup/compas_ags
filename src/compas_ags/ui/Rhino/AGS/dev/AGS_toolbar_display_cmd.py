from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas_ags.rhino import SettingsForm
from compas_ags.rhino import FormObject
from compas_ags.rhino import ForceObject


__commandname__ = "AGS_toolbar_display"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    if not scene:
        return

    # TODO: deal with undo redo
    SettingsForm.from_scene(scene, object_types=[FormObject, ForceObject], global_settings=['AGS'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
