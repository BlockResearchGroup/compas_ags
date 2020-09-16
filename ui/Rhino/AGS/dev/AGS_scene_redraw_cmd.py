from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_scene_redraw"


def RunCommand(is_interactive):

    sc.doc.EndUndoRecord(sc.doc.CurrentUndoRecordSerialNumber)

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    if not scene:
        return

    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
