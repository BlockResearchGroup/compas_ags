from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import scriptcontext as sc

import compas_rhino
import compas_ags

from compas_rhino.ui import CommandMenu
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.rhino import FormArtist


__commandname__ = "AGS_form_from"

HERE = compas_rhino.get_document_dirname()
HERE = HERE or os.path.dirname(compas_ags.__file__)

def create_formdiagram_from_lines(settings):
    guids = compas_rhino.select_lines(message='Select Form Diagram lines')
    if not guids:
        return
    lines = compas_rhino.get_line_coordinates(guids)
    graph = FormGraph.from_lines(lines)
    formdiagram = FormDiagram.from_graph(graph)
    return formdiagram


config = {
    "name": "create",
    "message": "Create formdiagram",
    "options": [
        {
            "name": "from_lines",
            "action": create_formdiagram_from_lines,
        },
}



def RunCommand(is_interactive):
    if 'AGS' not in sc.sticky:
        print("Initialise the plugin first!")
        return

    AGS = sc.sticky['AGS']
    settings = AGS['settings']
    formdiagram = AGS['formdiagram']

    menu = CommandMenu(config)
    action = menu.select_action()

    if action:
        del AGS['formdiagram']
        formdiagram = action["action"](settings)
        formartist = FormArtist(formdiagram, layer='FormDiagram')
        formartist.draw_vertices()
        formartist.draw_edges()
        formartist.draw_vertexlabels()
        formartist.draw_edgelabels()
        formartist.draw_facelabels()
        AGS['formdiagram'] = formdiagram