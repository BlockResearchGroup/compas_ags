from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import scriptcontext as sc

import compas_rhino
from compas.utilities import DataEncoder


__commandname__ = "AGS_session_save"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    system = sc.sticky['AGS']['system']
    scene = sc.sticky['AGS']['scene']

    filepath = compas_rhino.rs.SaveFileName('save', filter=system['session.extension'], folder=system['session.dirname'])

    if not filepath:
        return

    if filepath.split('.')[-1] != system['session.extension']:
        filepath = "%s.%s" % (filepath, system['session.extension'])

    dirname, basename = os.path.split(filepath)
    filename, _ = os.path.splitext(basename)

    system['session.dirname'] = dirname
    system['session.filename'] = filename

    filepath = os.path.join(dirname, filename + '.' + system['session.extension'])

    session = {
        "data": {"form": None, "force": None},
        "scene": {"form": None, "force": None}
    }

    objects = scene.find_by_name('Form')
    if objects:
        form = objects[0]
        if form:
            session['data']['form'] = form.diagram.to_data()
            session['scene']['form'] = {
                'settings': form.settings,
                'anchor': form.anchor,
                'location': form.location,
                'scale': form.scale
            }

    objects = scene.find_by_name('Force')
    if objects:
        force = objects[0]
        if force:
            session['data']['force'] = force.diagram.to_data()
            session['scene']['force'] = {
                'settings': force.settings,
                'anchor': force.anchor,
                'location': force.location,
                'scale': force.scale
            }

    with open(filepath, 'w+') as f:
        json.dump(session, f, cls=DataEncoder)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
