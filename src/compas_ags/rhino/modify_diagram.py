from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import rhinoscriptsyntax as rs

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
            'rhino_constraint_visualization',
            'get_initial_point',     
            'rhino_vertice_move',
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

    constraint_dict = {k:[False, False] for k in diagram.vertices()}

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt('Set Constraints.')

    boolOptionX = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionY = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
        
    while True:
        #select vertex
        vkey = VertexSelector.select_vertex(diagram, message='Select constraint vertex')
        if vkey is None:
            break
        
        # update constraint condition of selected vertex
        go.ClearCommandOptions()
        boolOptionX.CurrentValue = constraint_dict[vkey][0]
        boolOptionY.CurrentValue = constraint_dict[vkey][1]
        go.AddOptionToggle('fix_X', boolOptionX)
        go.AddOptionToggle('fix_Y', boolOptionY)

        opt = go.Get()
        if go.CommandResult() != Rhino.Commands.Result.Success:
            break
        if opt == Rhino.Input.GetResult.Option:
            # update constraint dictionary
            constraint_dict[vkey] = [boolOptionX.CurrentValue, boolOptionY.CurrentValue]
            print('current constraint', constraint_dict)
            continue # keep picking options
        break
    
    return constraint_dict



def rhino_constraint_visualization(diagram, layer=None):
    pass

    #--------------------------------------------------------------
    


    constraint_dict = {}

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt('Set Constraints.')

    boolOptionX = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionY = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
        
    while True:
        #select vertex
        vkey = VertexSelector.select_vertex(diagram, message='Select constraint vertex')
        if vkey is None:
            break
        
        # update constraint condition of selected vertex
        go.ClearCommandOptions()
        boolOptionX.CurrentValue = constraint_dict[vkey][0]
        boolOptionY.CurrentValue = constraint_dict[vkey][1]
        go.AddOptionToggle('fix_X', boolOptionX)
        go.AddOptionToggle('fix_Y', boolOptionY)

        opt = go.Get()
        if go.CommandResult() != Rhino.Commands.Result.Success:
            break
        if opt == Rhino.Input.GetResult.Option:
            # update constraint dictionary
            constraint_dict[vkey] = [boolOptionX.CurrentValue, boolOptionY.CurrentValue]
            x = diagram.vertex_coordinates(vkey)[0]
            y = diagram.vertex_coordinates(vkey)[1]
            s_pt = [x, y]
            e_pt = [x, y]
            print('current constraint', constraint_dict)
            continue # keep picking options
        break
    
    return constraint_dict

#--------------------------------------------------------------


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


def rhino_vertice_move(diagram):
    """Select diagram vertices and move them

    Parameters
    ----------
    diagram: compas_ags.formdiagram.FormDiagram / compas_ags.forcediagram.ForceDiagram 
        Diagram

    Return 
    ----------
    xy: list
        Dict contains new vertex keys and xy coordinates
    new_diagram:
        New diagram
    """

    vkeys = VertexSelector.select_vertices(diagram, message='Select vertice to move')

    anchor_key = diagram.anchor()
    print('anchor key is %s' % anchor_key) 
    print(vkeys)
    for vkey in vkeys:
        if vkey == anchor_key: print('it contains keys that should not be moved')

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

    
    # create a copy of the diagram
    new_diagram = diagram.copy()

    translation = target - ip
    xy = {}   # xy coordinates of targeted 
    for vkey in diagram.vertices():
        if vkey in vkeys:
            new_xyz = add_vectors(diagram.vertex_coordinates(vkey), translation)
            xy[vkey] = [new_xyz[0], new_xyz[1]]
            new_diagram.vertex[vkey]['constrained'] = False
            new_diagram.vertex[vkey]['x'] = new_xyz[0]
            new_diagram.vertex[vkey]['y'] = new_xyz[1]
            new_diagram.vertex[vkey]['z'] = new_xyz[2]
        else:
            xyz = diagram.vertex_coordinates(vkey)
            xy[vkey] = [xyz[0], xyz[1]]
    
    return xy, new_diagram


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':
    pass