from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math as m
import compas

from compas.geometry import add_vectors
from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector

from .conduit import ForceConduit, FormConduit

from System.Drawing.Color import FromArgb

try:
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    from Rhino.ApplicationSettings import *
    from Rhino.Geometry import Point3d

    from System.Drawing.Color import FromArgb

    dotted_color = FromArgb(0, 0, 0)
    arrow_color  = FromArgb(255, 0, 79)
    edge_color   = FromArgb(0, 0, 0)
    black          = FromArgb(0, 0, 0)
    gray           = FromArgb(200, 200, 200)
    white          = FromArgb(255, 255, 255)

except ImportError:
    compas.raise_if_ironpython()


__all__ = ['rhino_vertex_constraints', 
            'rhino_edge_constraints', 
               
            'move_force_vertice',
            'move_form_vertice',
            ]


def rhino_vertex_constraints(formdiagram, layer='constraints', scale=1.0):
    """ 
    Select vertices in the formdiagram and add constraints in x or y direction.

    Parameters
    ----------
    formdiagram : compas_ags.diagrams.FormDiagram
        The form diagram where vertices should be selected
    layer: string
        The layer name to draw constraints in rhino.
    scale: float
        The scale factor to visalize the constraint lines
    
    Return
    ------
    constraint_dict: dict
        key: int
            vertex key of vertices in the formdiagram
        value: [Boolean, Boolean], default: [False, False]
            whether the vertex is constrained in x direction, y direction
            for example, if a vertex is constrained in x but not y: [True, False]

    """
    # check the layers to draw constraint lines
    from Rhino.DocObjects.ObjectColorSource import ColorFromObject
    import copy

    layer_index = sc.doc.Layers.FindByFullPath(layer, True)
    # clear layer
    if layer_index >= 0: 
        rhobjs = sc.doc.Objects.FindByLayer(layer)
        rs.DeleteObjects(rhobjs)
    # if the layer doesn't exist, create a new one
    else:
        new_layer = Rhino.DocObjects.Layer()
        new_layer.Name = layer
        layer_index = sc.doc.Layers.Add(new_layer)

    # update the fixed vertices
    fixed = formdiagram.fixed()
    constraint_dict = {k:[False, False] for k in formdiagram.vertices()}
    formdiagram.vertices_attribute('_fixed_X', False)
    formdiagram.vertices_attribute('_fixed_Y', False)
    lines_dict =  {k:[None, None] for k in formdiagram.vertices()}

    def draw_lines(x_s, y_s, x_e, y_e, **kwargs):
        color=(255, 0, 0)  # color to show constraints
        guid = sc.doc.Objects.AddLine(Point3d(x_s, y_s, 0), Point3d(x_e, y_e, 0))
        obj = sc.doc.Objects.Find(guid)
        attr = obj.Attributes
        attr.ObjectColor = FromArgb(*color)
        attr.ColorSource = ColorFromObject
        attr.LayerIndex = layer_index
        obj.CommitChanges()
        return obj

    for vkey in fixed:
        constraint_dict[vkey] = [True, True]
        formdiagram.vertex_attribute(vkey, '_fixed_X', True)
        formdiagram.vertex_attribute(vkey, '_fixed_Y', True)
        x = formdiagram.vertex_coordinates(vkey)[0]
        y = formdiagram.vertex_coordinates(vkey)[1]
        s_pt = [x, y]
        e_pt = [x, y]
        x_s = s_pt[0] - 1 * scale
        x_e = e_pt[0] + 1 * scale
        y_s = s_pt[1] - 1 * scale
        y_e = e_pt[1] + 1 * scale
        obj_x = draw_lines(x_s, s_pt[1], x_e, e_pt[1])
        obj_y = draw_lines(s_pt[0], y_s, e_pt[0], y_e)
        lines_dict[vkey][0] = obj_x
        lines_dict[vkey][1] = obj_y
        sc.doc.Views.Redraw()

    constraint_dict_copy = copy.deepcopy(constraint_dict) # to check the last change of the dict

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt('Set Constraints.')

    boolOptionX = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionY = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')

    while True:
        #select vertex
        vkey = VertexSelector.select_vertex(formdiagram, message='Select constraint vertex')
        if vkey is None:
            print('Nothing is selected. End of selection.')
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
            _fore_constrint = constraint_dict_copy[vkey]

            x = formdiagram.vertex_coordinates(vkey)[0]
            y = formdiagram.vertex_coordinates(vkey)[1]
            s_pt = [x, y]
            e_pt = [x, y]

            # add x constraint
            if _fore_constrint[0] is False and boolOptionX.CurrentValue is True:
                s_pt[0] -= 1 * scale
                e_pt[0] += 1 * scale
                obj = draw_lines(s_pt[0], s_pt[1], e_pt[0], e_pt[1])
                lines_dict[vkey][0] = obj
                sc.doc.Views.Redraw()

            # add y constraint
            elif _fore_constrint[1] is False and boolOptionY.CurrentValue is True:
                s_pt[1] -= 1 * scale
                e_pt[1] += 1 * scale
                obj = draw_lines(s_pt[0], s_pt[1], e_pt[0], e_pt[1])
                lines_dict[vkey][1] = obj
                sc.doc.Views.Redraw()

            # remove x constraints
            elif _fore_constrint[0] is True and boolOptionX.CurrentValue is False:
                obj = lines_dict[vkey][0]
                sc.doc.Objects.Delete(obj)
                lines_dict[vkey][0] = None
                sc.doc.Views.Redraw()

            # remove y constraints
            elif _fore_constrint[1] is True and boolOptionY.CurrentValue is False:
                obj = lines_dict[vkey][1]
                sc.doc.Objects.Delete(obj)
                lines_dict[vkey][1] = None
                sc.doc.Views.Redraw()

            constraint_dict_copy[vkey] = [boolOptionX.CurrentValue, boolOptionY.CurrentValue]
            formdiagram.vertex_attribute(vkey, '_fixed_X', boolOptionX.CurrentValue)
            formdiagram.vertex_attribute(vkey, '_fixed_Y', boolOptionY.CurrentValue)

            print('current constraint', constraint_dict)
            continue # keep picking options
        break

    constraint_dict = {key: [formdiagram.vertex_attribute(key, '_fixed_X') , formdiagram.vertex_attribute(key, '_fixed_Y')] for key in formdiagram.vertices()}

    return constraint_dict


def rhino_edge_constraints(formdiagram):
    """set edge constraints in Rhino: fix length of an edge 

    Parameters
    ----------
    formdiagram: compas_ags.diagrams.FormDiagram
        The diagram where vertices need to be fixed
    
    Return 
    ----------
    constraint_dict: dict
        key: int
            vertex key of the edge
        value: boolean
            True: length of the edge is fixed 
    """

    constraint_dict = {}

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt('Set Constraints')

    boolOptionL = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    go.AddOptionToggle('fix_length', boolOptionL)

    while True:
        uv = EdgeSelector.select_edge(formdiagram, message='Select constraint edge')
        if uv is None:
            print('Nothing is selected. End of selection.')
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


def move_force_vertice(forcediagram, diagramartist):
    """Move vertices of the force diagram

    Parameters
    ----------
    forcediagram: compas_ags.diagrams.ForceDiagram
        The force diagram whose vertices need to be moved
    diagramartist: compas_ags.rhino.ForceArtist
        The ForceArtist to draw the diagram
    
    Return 
    ------
    xy: dict
        key: int
            vertex key of the edge
        value: [x_coordinate, y_coordinate]
            A list contains x and y coordinates of the updated force diagram
    forcediagram: compas_ags.diagrams.ForceDiagram
        The updated force diagram
    """

    anchor_key = forcediagram.anchor()
    dx = forcediagram.vertex_coordinates(anchor_key)[0]
    dy = forcediagram.vertex_coordinates(anchor_key)[1]
    print('anchor key is %s' % anchor_key) 
    sca_factor = diagramartist.scale
    print('scale factor of force diagram is', sca_factor)

    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        translation = cp - ip
        for vkey in vkeys:
            xyz = forcediagram.vertex_coordinates(vkey)
            x_trans = dx + (xyz[0] - dx) / sca_factor
            y_trans = dy + (xyz[1] - dy) / sca_factor
            sp  = Point3d(x_trans, y_trans, 0)
            for nbr_vkey in nbr_vkeys[vkey]:
                nbr  = forcediagram.vertex_coordinates(nbr_vkey)
                nbr_x_trans = dx + (nbr[0] - dx) / sca_factor
                nbr_y_trans = dy + (nbr[1] - dy) / sca_factor
                np   = Point3d(nbr_x_trans, nbr_y_trans, 0)
                line = Rhino.Geometry.Line(sp, sp + translation)
                e.Display.DrawDottedLine(np, sp + translation, dotted_color)
                e.Display.DrawArrow(line, arrow_color, 15, 0)

                # display force magnitudes
                dis_real = m.sqrt((cp[0] - nbr_x_trans) ** 2 + (cp[1] - nbr_y_trans) ** 2) * sca_factor
                dot_x = (cp[0] - nbr_x_trans) / 2 + nbr_x_trans
                dot_y = (cp[1] - nbr_y_trans) / 2 + nbr_y_trans
                e.Display.DrawDot(Point3d(dot_x, dot_y, 0), '%s kN' % (round(dis_real, 2)), gray, white)

        for pair in list(edges):
            pair = list(pair)
            u  = forcediagram.vertex_coordinates(pair[0])
            v  = forcediagram.vertex_coordinates(pair[1])
            u_x_trans = dx + (u[0] - dx) / sca_factor
            u_y_trans = dy + (u[1] - dy) / sca_factor
            v_x_trans = dx + (v[0] - dx) / sca_factor
            v_y_trans = dy + (v[1] - dy) / sca_factor
            sp = Point3d(u_x_trans, u_y_trans, 0) + translation
            ep = Point3d(v_x_trans, v_y_trans, 0) + translation
            e.Display.DrawLine(sp, ep, edge_color, 3)
    
    # xy coordinates of targeted 
    xy = {} 
    for vkey in forcediagram.vertices():
        xyz = forcediagram.vertex_coordinates(vkey)
        xy[vkey] = [xyz[0], xyz[1]]

    rs.EnableRedraw(True)
    conduit = ForceConduit(forcediagram)
    
    while True:
        vkeys = VertexSelector.select_vertices(forcediagram, message='Select force diagram vertices to move')
        if vkeys == []:
            break
        vkeys = set(vkeys)
        print(vkeys, 'these keys are selected')

        nbr_vkeys = {}
        edges = set()
        for vkey in vkeys:
            all_nbrs = forcediagram.vertex_neighbors(vkey)
            nbrs = []
            for nbr in all_nbrs:
                if nbr in vkeys:
                    edges.add(frozenset([vkey, nbr]))
                else:
                    nbrs.append(nbr)
            nbr_vkeys[vkey] = nbrs

        # get the point to move from 
        ip = get_initial_point()

        gp = Rhino.Input.Custom.GetPoint()
        gp.PermitOrthoSnap(True)
        gp.DynamicDraw += OnDynamicDraw
        gp.SetCommandPrompt('Point to move to')

        while True:
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
        translation_real_scale = [t * sca_factor for t in translation]
        for vkey in forcediagram.vertices():
            if vkey in vkeys:
                new_xyz = add_vectors(forcediagram.vertex_coordinates(vkey), translation_real_scale)
                xy[vkey] = [new_xyz[0], new_xyz[1]]
                forcediagram.vertex[vkey]['constrained'] = False
                forcediagram.vertex[vkey]['x'] = new_xyz[0]
                forcediagram.vertex[vkey]['y'] = new_xyz[1]
                forcediagram.vertex[vkey]['z'] = new_xyz[2]

        conduit.redraw()
        continue

    rs.EnableRedraw(False)
    return xy, forcediagram


def move_form_vertice(formdiagram, diagramartist):
    """Move vertices of the form diagram

    Parameters
    ----------
    formdiagram: compas_ags.diagrams.FormDiagram
        The form diagram whose vertices need to be moved
    diagramartist: compas_ags.rhino.FormArtist
        The FormArtist to draw the diagram
    
    Return 
    ------
    xy: dict
        key: int
            vertex key of the edge
        value: [x_coordinate, y_coordinate]
            A list contains x and y coordinates of the updated form diagram
    formdiagram: compas_ags.diagrams.FormDiagram
        The updated form diagram
    """

    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        translation = cp - ip
        for vkey in vkeys:
            xyz = formdiagram.vertex_coordinates(vkey)
            sp  = Point3d(*xyz)
            for nbr_vkey in nbr_vkeys[vkey]:
                nbr  = formdiagram.vertex_coordinates(nbr_vkey)
                np   = Point3d(*nbr)
                line = Rhino.Geometry.Line(sp, sp + translation)
                e.Display.DrawDottedLine(np, sp + translation, dotted_color)
                e.Display.DrawArrow(line, arrow_color, 15, 0)

        for pair in list(edges):
            pair = list(pair)
            u  = formdiagram.vertex_coordinates(pair[0])
            v  = formdiagram.vertex_coordinates(pair[1])
            sp = Point3d(*u) + translation
            ep = Point3d(*v) + translation
            e.Display.DrawLine(sp, ep, edge_color, 3)

    fixed_key = formdiagram.fixed()
    print('fixed key is %s' % fixed_key) 
    
    # xy coordinates of targeted 
    xy = {} 
    for vkey in formdiagram.vertices():
        xyz = formdiagram.vertex_coordinates(vkey)
        xy[vkey] = [xyz[0], xyz[1]]

    rs.EnableRedraw(True)
    conduit = FormConduit(formdiagram)
    
    while True:
        vkeys = VertexSelector.select_vertices(formdiagram, message='Select vertices to move')
        if vkeys == []:
            break
        nbr_vkeys = {}
        edges = set()
        for vkey in vkeys:
            all_nbrs = formdiagram.vertex_neighbors(vkey)
            nbrs = []
            for nbr in all_nbrs:
                if nbr in vkeys:
                    edges.add(frozenset([vkey, nbr]))
                else:
                    nbrs.append(nbr)
            nbr_vkeys[vkey] = nbrs
        
        # get the point to move from 
        ip = get_initial_point()

        gp = Rhino.Input.Custom.GetPoint()
        gp.DynamicDraw += OnDynamicDraw
        gp.SetCommandPrompt('Point to move to')

        while True:
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
        
        for vkey in formdiagram.vertices():
            if vkey in vkeys:
                new_xyz = add_vectors(formdiagram.vertex_coordinates(vkey), translation)
                xy[vkey] = [new_xyz[0], new_xyz[1]]
                formdiagram.vertex[vkey]['constrained'] = False
                formdiagram.vertex[vkey]['x'] = new_xyz[0]
                formdiagram.vertex[vkey]['y'] = new_xyz[1]
                formdiagram.vertex[vkey]['z'] = new_xyz[2]

        conduit.redraw()
        continue

    rs.EnableRedraw(False)
    return xy, formdiagram


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':
    pass