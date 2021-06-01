from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import webbrowser

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_docs"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    webbrowser.open('https://blockresearchgroup.github.io/compas_ags/')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
