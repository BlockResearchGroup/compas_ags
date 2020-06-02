from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas

from compas.geometry import add_vectors
from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector

try:
    import Rhino
    from Rhino.ApplicationSettings import *
    from Rhino.Geometry import Point3d

    from System.Drawing.Color import FromArgb

    dotted_color = FromArgb(0, 0, 0)
    arrow_color  = FromArgb(255, 0, 79)
    edge_color   = FromArgb(0, 0, 0)

except ImportError:
    compas.raise_if_ironpython()


__all__ = ['rhino_vertex_constraints', 
            'rhino_edge_constraints', 
            'get_initial_point',     
            'rhino_vertex_move',
            ]


def rhino_vertex_constraints(diagram):
    """set vertex constraints in Rhino: fix vertex x, y coordinates 

    Parameters
    ----------
    diagram: compas_ags.formdiagram.FormDiagram
        The diagram where vertices need to be fixed
    
    Return 
    ----------
    constraint_dict: dict
        key: int
            vertex key of the digram
        value: [boolean, boolean]
            x,y fixed is True, not fixed is false
    """

    constraint_dict = {}

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt('Set Constraints')

    boolOptionX = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionY = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')

    go.AddOptionToggle('fix_X', boolOptionX)
    go.AddOptionToggle('fix_Y', boolOptionY)
        
    while True:
        vkey = VertexSelector.select_vertex(diagram, message='Select constraint vertex')
        if vkey is None:
            break
        opt = go.Get()
        if go.CommandResult() != Rhino.Commands.Result.Success:
            break
        if opt == Rhino.Input.GetResult.Option:  # keep picking options
            constraint_dict[vkey] = [boolOptionX.CurrentValue, boolOptionY.CurrentValue]
            continue
        break
    
    return constraint_dict


def rhino_edge_constraints(diagram):
    """set edge constraints in Rhino: fix length of an edge 

    Parameters
    ----------
    diagram: compas_ags.formdiagram.FormDiagram
        The diagram where vertices need to be fixed
    
    Return 
    ----------
    constraint_dict: dict
        key: int
            vertex key of the edge
        value: boolean
            True: length of the edge is fixed 

    TODO??: SET EDGE LENGTH
    """

    constraint_dict = {}

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt('Set Constraints')

    boolOptionL = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    go.AddOptionToggle('fix_length', boolOptionL)

    while True:
        uv = EdgeSelector.select_edge(diagram, message='Select constraint edge')
        print(uv)
        if uv is None:
            break
        opt = go.Get()
        if go.CommandResult() != Rhino.Commands.Result.Success:
            break
        if opt == Rhino.Input.GetResult.Option:  # keep picking options
            constraint_dict[uv] = boolOptionL.CurrentValue
            continue
        break
    
    return constraint_dict


def get_initial_point(message='Point to move from?'):
    ip = Rhino.Input.Custom.GetPoint()
    ip.SetCommandPrompt(message)
    ip.Get()
    ip = ip.Point()
    return ip


def rhino_vertex_move(diagram):
    vkeys = VertexSelector.select_vertices(diagram)

    nbr_vkeys = {}
    edges = set()
    for vkey in vkeys:
        all_nbrs = diagram.vertex_neighbors(vkey)
        nbrs = []
        for nbr in all_nbrs:
            if nbr in vkeys:
                edges.add(frozenset([vkey, nbr]))
            else:
                nbrs.append(nbr)
        nbr_vkeys[vkey] = nbrs

    ip = get_initial_point()

    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        translation = cp - ip
        for vkey in vkeys:
            xyz = diagram.vertex_coordinates(vkey)
            sp  = Point3d(*xyz)
            for nbr_vkey in nbr_vkeys[vkey]:
                nbr  = diagram.vertex_coordinates(nbr_vkey)
                np   = Point3d(*nbr)
                line = Rhino.Geometry.Line(sp, sp + translation)
                e.Display.DrawDottedLine(np, sp + translation, dotted_color)
                e.Display.DrawArrow(line, arrow_color, 15, 0)

        for pair in list(edges):
            pair = list(pair)
            u  = diagram.vertex_coordinates(pair[0])
            v  = diagram.vertex_coordinates(pair[1])
            sp = Point3d(*u) + translation
            ep = Point3d(*v) + translation
            e.Display.DrawLine(sp, ep, edge_color, 3)

    ModelAidSettings.Ortho = True
    gp = Rhino.Input.Custom.GetPoint()
    gp.DynamicDraw += OnDynamicDraw
    gp.SetCommandPrompt('Point to move to')
    ortho_option = Rhino.Input.Custom.OptionToggle(True, 'Off', 'On')
    gp.AddOptionToggle('ortho_snap', ortho_option)

    while True:
        # ModelAidSettings.Ortho = ortho_option.CurrentValue
        get_rc = gp.Get()
        gp.SetBasePoint(ip, False)
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            continue
        if get_rc == Rhino.Input.GetResult.Option:
            continue
        elif get_rc == Rhino.Input.GetResult.Point:
            target = gp.Point()
        break

    translation = target - ip
    for vkey in vkeys:
        new_xyz = add_vectors(diagram.vertex_coordinates(vkey), translation)
        diagram.vertex_update_xyz(vkey, new_xyz, constrained=False)

# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':
    pass