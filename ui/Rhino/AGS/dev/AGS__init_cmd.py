from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import errno
import shelve

import scriptcontext as sc

import compas
import compas_rhino

from compas.rpc import Proxy
from compas_ags.rhino import Scene
from compas_ags.web import Browser


__commandname__ = "AGS__init"


# the current working directory could be the APPTEMP directory for AGS
# until it is specified by the user
HERE = compas_rhino.get_document_dirname()
HOME = os.path.expanduser('~')
CWD = HERE or HOME


SETTINGS = {
    'AGS': {
        'autoupdate': True,
    }
}


def RunCommand(is_interactive):

    shelvepath = os.path.join(compas.APPTEMP, 'AGS', '.history')
    if not os.path.exists(os.path.dirname(shelvepath)):
        try:
            os.makedirs(os.path.dirname(shelvepath))
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

    db = shelve.open(shelvepath, 'n')
    db['states'] = []

    scene = Scene(db, 20, SETTINGS)
    scene.purge()

    sc.sticky["AGS"] = {
        'proxy': Proxy(),
        'system': {
            "session.dirname": CWD,
            "session.filename": None,
            "session.extension": 'ags'
        },
        'scene': scene,
    }

    scene.update()

    # would be useful to add a notification about the cloud: new / reconnect
    # compas_rhino.display_message("AGS has started.")
    Browser()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
