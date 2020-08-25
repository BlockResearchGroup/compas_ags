from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import scriptcontext as sc

import compas_rhino

from compas.utilities import DataDecoder

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram


__commandname__ = "AGS_session_load"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    system = sc.sticky['AGS']['system']
    scene = sc.sticky['AGS']['scene']

    filepath = compas_rhino.select_file(folder=system['session.dirname'], filter=system['session.extension'])

    if not filepath:
        return
    if not os.path.exists(filepath):
        return
    if not os.path.isfile(filepath):
        return
    if not filepath.endswith(".{}".format(system['session.extension'])):
        return

    dirname, basename = os.path.split(filepath)
    filename, extension = os.path.splitext(basename)

    system['session.dirname'] = dirname
    system['session.filename'] = filename

    with open(filepath, "r") as f:
        session = json.load(f, cls=DataDecoder)

    if not session['data']['form']:
        compas_rhino.display_message('The session file has no form diagram.')

    formdiagram = FormDiagram.from_data(session['data']['form'])

    form_id = scene.add(formdiagram, name='Form', layer='AGS::FormDiagram')
    form = scene.find(form_id)

    if 'anchor' in session['scene']['form']:
        form.artist.anchor_vertex = session['scene']['form']['anchor']['vertex']
        form.artist.anchor_point = session['scene']['form']['anchor']['point']

    if 'scale' in session['scene']['form']:
        form.artist.scale = session['scene']['form']['scale']

    if session['data']['force']:
        forcediagram = ForceDiagram.from_data(session['data']['force'])

        forcediagram.dual = formdiagram
        formdiagram.dual = forcediagram

        force_id = scene.add(forcediagram, name='Force', layer='AGS::ForceDiagram')
        force = scene.find(force_id)

        if 'anchor' in session['scene']['force']:
            force.artist.anchor_vertex = session['scene']['force']['anchor']['vertex']
            force.artist.anchor_point = session['scene']['force']['anchor']['point']

        if 'scale' in session['scene']['form']:
            force.artist.scale = session['scene']['force']['scale']

    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
