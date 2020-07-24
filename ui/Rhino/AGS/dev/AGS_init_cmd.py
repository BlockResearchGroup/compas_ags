from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import scriptcontext as sc

import compas_rhino

from compas.rpc import Proxy
from compas_ags.rhino import Scene


__commandname__ = "AGS_init"


HERE = compas_rhino.get_document_dirname()
HOME = os.path.expanduser('~')
CWD = HERE or HOME


def RunCommand(is_interactive):

    scene = Scene()
    scene.clear()

    sc.sticky["AGS"] = {
        'proxy': Proxy(),
        'system': {
            "session.dirname": CWD,
            "session.filename": None,
            "session.extension": 'ags'
        },
        'scene': scene
    }


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
