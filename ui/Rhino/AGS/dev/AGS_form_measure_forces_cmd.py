from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_force_measure_forces"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    form = objects[0]

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    force = objects[0]

    scale = force.scale
    form.settings['show.edges'] = True
    form.settings['show.forcelabels'] = False
    form.settings['show.edgelabels'] = False
    scene.update()

    while True:
        edge = form.select_edge()
        if not edge:
            break

        edge_index = form.diagram.edge_index()
        index = edge_index[edge]

        f = form.diagram.edge_attribute(edge, 'f')
        l = f * scale

        text = {edge: "{:.4g}kN".format(abs(f))}
        color = {}
        tol = form.settings['tol.forces']

        if form.diagram.edge_attribute(edge, 'is_external'):
            color[edge] = form.settings['color.edges:is_external']
        if form.diagram.edge_attribute(edge, 'is_load'):
            color[edge] = form.settings['color.edges:is_load']
        if form.diagram.edge_attribute(edge, 'is_reaction'):
            color[edge] = form.settings['color.edges:is_reaction']
        if form.diagram.edge_attribute(edge, 'is_ind'):
            color[edge] = form.settings['color.edges:is_ind']

        if not form.diagram.edge_attribute(edge, 'is_external'):
            if f > + tol:
                color[edge] = form.settings['color.tension']
            elif f < - tol:
                color[edge] = form.settings['color.compression']

        guid_edgelabel = form.artist.draw_edgelabels(text=text, color=color)
        form.guid_edgelabel = zip(guid_edgelabel, edge)
        form.redraw()

        compas_rhino.display_message("Edge Index: {0}\nForce Diagram Edge Length: {1:.3g}m\nForce Drawing Scale: {2:.3g}\nForce Magnitude: {3:.3g}kN".format(index, l, scale, f))

        answer = compas_rhino.rs.GetString("Continue selecting edges?", "No", ["Yes", "No"])
        if not answer:
            break
        if answer == "No":
            break
        if answer == 'Yes':
            scene.update()

    form.settings['show.forcelabels'] = True

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
