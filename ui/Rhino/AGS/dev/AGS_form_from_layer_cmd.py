from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import rhinoscriptsyntax as rs
import compas_rhino

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas.geometry import Line
from compas.geometry import is_point_on_line
from compas_rhino.utilities import get_object_layers

__commandname__ = "AGS_form_from_layer"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    system = sc.sticky['AGS']['system']
    scene = sc.sticky['AGS']['scene']


    layer = rs.CurrentLayer()
    layer_name = compas_rhino.rs.GetString("Layer to construct FormDiagram", layer)
    guids = compas_rhino.get_lines(layer=layer_name)
    if not guids:
        return
    rs.HideObjects(guids)
    lines = compas_rhino.get_line_coordinates(guids)
    graph = FormGraph.from_lines(lines)

     # check planarity
     
    if not graph.is_planar_embedding():
        raise ValueError("The graph is not planar. Check your graph!")

    form = FormDiagram.from_graph(graph)

    scene.add(form, name='Form', layer='AGS::FormDiagram')

    scene.clear()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
