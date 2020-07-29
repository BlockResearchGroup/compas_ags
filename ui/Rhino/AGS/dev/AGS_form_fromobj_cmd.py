from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram


__commandname__ = "AGS_form_fromobj"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    system = sc.sticky['AGS']['system']
    scene = sc.sticky['AGS']['scene']

    filepath = compas_rhino.browse_for_file('Select an input file.', folder=system['session.dirname'], filter='obj')

    if filepath:
        graph = FormGraph.from_obj(filepath)
        
        # check planarity
        if not graph.is_planar_embedding():
            raise ValueError("The graph is not planar. Check your graph!")
        # check L-nodes
        from compas.geometry import Line
        from compas.geometry import is_point_on_line

        nodes_to_del = []
        # check the node that can never achieve equilibrium
        for key in graph.nodes():
            if graph.degree(key) == 2:
                nbrs = graph.neighborhood(key)
                line = Line(graph.node_coordinates(nbrs[0]), graph.node_coordinates(nbrs[1]))
                node = graph.node_coordinates(key)
                if not is_point_on_line(node, line):
                    print("this node %s can never achieve equilibrium" % key)
                    nodes_to_del.append(key)

        if len(nodes_to_del) != 0:
            print('The form diagram is reconstructed.....')
            for key in nodes_to_del:
                graph.delete_node(key)
            # reconstrcut the network for new keys, new keys don't correspond in cycle faces.
            lines = graph.to_lines()
            graph = FormGraph.from_lines(lines)

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
