from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas.geometry import Line
from compas.geometry import is_point_on_line

__commandname__ = "AGS_form_fromobj"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    system = sc.sticky['AGS']['system']
    scene = sc.sticky['AGS']['scene']

    filepath = compas_rhino.browse_for_file('Select an input file.', folder=system['session.dirname'], filter='json')

    if not filepath:
        return 

    graph = FormGraph.from_json(filepath)
    
    form = FormDiagram.from_graph(graph)
    # force = ForceDiagram.from_formdiagram(form)

    scene.add(form, name='Form', layer='AGS::FormDiagram')
    # scene.add(force, name='Force', layer='AGS::ForceDiagram')

    scene.clear()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
