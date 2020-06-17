from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from ast import literal_eval

import compas
import compas_rhino

from compas.utilities import flatten
from compas.utilities import geometric_key
from compas.utilities import i_to_rgb

from compas_rhino.geometry import RhinoPoint
from compas_rhino.geometry import RhinoCurve

from compas_rhino.modifiers import VertexModifier
from compas_rhino.modifiers import EdgeModifier
from compas_rhino.modifiers import FaceModifier

from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector
from compas_rhino.selectors import FaceSelector

try:
    import Rhino
    from Rhino.Geometry import Point3d
    import scriptcontext as sc
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()


__all__ = ['DiagramHelper',
            'display_nullspace_rhino',
            'select_forcediagram_location', 
            'select_loaded_edges', 
            'select_fixed_vertices',
            'set_edge_loads',
            'diagram_fix_vertice', 
            'check_edge_pairs', 
            'find_force_ind', 
            'draw_dual_form_faces_force_vertices',
            'draw_dual_form_vertices_force_faces',
            'draw_dual_edges', 
            ]


def display_nullspace_rhino(diagram, nullspace, i):
    if i >= len(nullspace):
        raise ValueError
    else:
        c = 10
        nsi = nullspace[i] 

        # store lines representing the current null space mode
        form_lines = []
        keys = list(diagram.edges())
        for (u, v) in keys:
            sp = [x + y * c for x, y in zip(diagram.vertex_coordinates(u, 'xy'),  nsi[u])]
            sp.append(0)
            ep = [x + y * c for x, y in zip(diagram.vertex_coordinates(v, 'xy'),  nsi[v])]
            ep.append(0)
            line = {}
            line['start'] = sp
            line['end'] = ep
            form_lines.append(line)
        compas_rhino.draw_lines(form_lines, layer='nullspace', clear=False, redraw=False)


def select_forcediagram_location(force):
    # can ask for user to input a location
    force_point = rs.GetPoint("Set Force Diagram Location")
    force.set_anchor([0])
    force.vertex_attribute(0, 'x', force_point[0])  
    force.vertex_attribute(0, 'y', force_point[1])


def select_fixed_vertices(form):
    guids = compas_rhino.select_points(message='Select Fix Vertice')
    pts = compas_rhino.get_point_coordinates(guids)
    gkey_key = form.gkey_key()
    for pt in pts:
        vkey = gkey_key[geometric_key(pts)]
        print(vkey)
        form.vertex_attribute(vkey, 'is_fixed', True)


def diagram_fix_vertice(diagram):
    vkeys = VertexSelector.select_vertices(diagram, message='Select vertice to fix')
    for vkey in vkeys:
        diagram.vertex_attribute(vkey, 'is_fixed', True)
    print(vkeys)
    return vkeys


def set_edge_loads(form):
    # select multiple independent edges and set forces
    while True:
        edges = EdgeSelector.select_edges(form, message='Select Loaded Edge')
        if edges == []:
            print('Nothing is selected. End of selection.')
            break
        force_value = rs.GetReal("Force on Edges", 1.0)
        for (u, v) in edges: 
            form.set_edge_force(u, v, force_value)
        

def select_loaded_edges(form):
    guids = compas_rhino.select_lines(message='Select Loaded Edges')
    lines = compas_rhino.get_line_coordinates(guids)
    gkey_key = form.gkey_key()
    uv_i = form.uv_index()
    for p1,p2 in lines:
        u = gkey_key[geometric_key(p1)]
        v = gkey_key[geometric_key(p2)]
        print(u,v)
        try:
            index = uv_i[(u, v)]
            uv = (u, v)
            return index, uv
        except:
            index = uv_i[(v, u)]
            vu = (v, u)
            return index, vu


def check_edge_pairs(form, force):
    """check the uv direction in force diagrams
    
    return edge uv that need to be flipped in force digram
    and edge index corresponding to the form diagram
    """

    from compas.geometry import  dot_vectors
    edges_to_flip = []
    form_edges = {uv: index for index, uv in enumerate(form.edges())}
    force_edgelabel_pairs = {}
    for i, (u, v) in enumerate(force.edges()):
        force_vector = force.edge_vector(u, v)
        half_edge = form.face_adjacency_halfedge(u, v)

        if half_edge in form_edges:
            form_vector = form.edge_vector(half_edge[0], half_edge[1])
            dot_product = dot_vectors(form_vector, force_vector)
            force_in_form = form.edge_attribute(half_edge, 'f')
            if force_in_form * dot_product < 0:
                edges_to_flip.append((u, v))

        else:
            half_edge = form.face_adjacency_halfedge(v, u)
            form_vector = form.edge_vector(half_edge[0], half_edge[1])
            dot_product = dot_vectors(form_vector, force_vector)
            force_in_form = form.edge_attribute(half_edge, 'f')
            if force_in_form * dot_product < 0:
                edges_to_flip.append((u, v))

        force_edgelabel_pairs[u,v] = form_edges[half_edge]

    return edges_to_flip, force_edgelabel_pairs


def find_force_ind(form, force):
        # check the corresponding independent edges in the force diagram
        force_idx_uv = {idx:uv for uv, idx in check_edge_pairs(form, force)[1].items()}
        form_index_uv = form.index_uv()

        force_ind = []
        for idx in list(force_idx_uv.keys()):
            u, v = form_index_uv[idx]
            if (u, v) in form.ind():
                force_ind.append(force_idx_uv[idx])
        return force_ind


def draw_dual_form_faces_force_vertices(form, force, formartist, forceartist, color_scheme=i_to_rgb):
    c_dict  = {}
    for i, fkey in enumerate(form.faces()):
        value = float(i) / (form.number_of_faces() - 1)
        color = color_scheme(value)
        c_dict[fkey] = color
    
    formartist.draw_edges()
    formartist.draw_faces(color=c_dict)
    formartist.draw_facelabels()

    forceartist.draw_edges()
    forceartist.clear_vertexlabels()
    forceartist.draw_vertexlabels(color=c_dict)


def draw_dual_form_vertices_force_faces(form, force, formartist, forceartist, color_scheme=i_to_rgb):
    c_dict  = {}
    if force.number_of_faces() == 1:
        c_dict[list(force.faces())[0]] = color_scheme(1.0)
    else:
        for i, fkey in enumerate(force.faces()):
            value = float(i) / (force.number_of_faces() - 1)
            color = color_scheme(value)
            c_dict[fkey] = color
    formartist.draw_edges()
    formartist.clear_vertexlabels()
    formartist.draw_vertexlabels(color=c_dict)

    forceartist.draw_edges()
    forceartist.draw_faces(color=c_dict)
    forceartist.draw_facelabels()


def draw_dual_edges(form, force, formartist, forceartist, color_scheme=i_to_rgb, show_forces=False):
    """visualize dual edges
    color gradient corresponds to force magnitude in the edge
    """
    form_c_dict = {}
    if show_forces is True:
        force_c_dict = forceartist.draw_edge_force(draw=True)
    else:
        force_c_dict = forceartist.draw_edge_force(draw=False)
    force_uv_form_idx_pairs = check_edge_pairs(form, force)[1]
    for force_uv, form_idx in iter(force_uv_form_idx_pairs.items()):
        form_uv = list(form.edges())[form_idx]
        form_c_dict[form_uv] = force_c_dict[force_uv]
    
    formartist.draw_edges()
    formartist.draw_edgelabels(text={uv: index for index, uv in enumerate(form.edges())}, color=form_c_dict)
    forceartist.draw_edges()
    forceartist.draw_edgelabels(text=force_uv_form_idx_pairs, color=force_c_dict)


def match_edges(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.edge.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')[2].split('-')
        u = literal_eval(parts[0])
        v = literal_eval(parts[1])
        if (u, v) in keys or (v, u) in keys:
            guids.append(guid)
    return guids


def match_vertices(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.vertex.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


class DiagramHelper(VertexSelector,
                    EdgeSelector,
                    FaceSelector,
                    VertexModifier,
                    EdgeModifier,
                    FaceModifier):

    @staticmethod
    def highlight_edges(diagram, keys):
        guids = match_edges(diagram, keys)
        rs.EnableRedraw(False)
        rs.SelectObjects(guids)
        rs.EnableRedraw(True)

    @staticmethod
    def unhighlight_edges(diagram, keys):
        guids = match_edges(diagram, keys)
        rs.EnableRedraw(False)
        rs.UnselectObjects(guids)
        rs.EnableRedraw(True)

    @staticmethod
    def highlight_vertices(diagram, keys):
        guids = match_vertices(diagram, keys)
        rs.EnableRedraw(False)
        rs.SelectObjects(guids)
        rs.EnableRedraw(True)

    @staticmethod
    def unhighlight_vertices(diagram, keys):
        guids = match_vertices(diagram, keys)
        rs.EnableRedraw(False)
        rs.UnselectObjects(guids)
        rs.EnableRedraw(True)

    @staticmethod
    def select_vertices_where(diagram, keys):
        rs.UnselectAllObjects()
        DiagramHelper.highlight_vertices(diagram, keys)

    @staticmethod
    def select_vertices_on_boundary(diagram):
        rs.UnselectAllObjects()
        key = DiagramHelper.select_vertex(diagram)
        if key is None:
            return
        boundaries = diagram.vertices_on_boundaries()
        for boundary in boundaries:
            if key in boundary:
                DiagramHelper.highlight_vertices(diagram, boundary)
                return boundary

    @staticmethod
    def select_vertices_on_curve(diagram):
        rs.UnselectAllObjects()
        guid = compas_rhino.select_curve()
        keys = DiagramHelper.identify_vertices_on_curve(diagram, guid)
        DiagramHelper.highlight_vertices(diagram, keys)
        return keys

    @staticmethod
    def select_vertices_on_curves(diagram):
        rs.UnselectAllObjects()
        guids = compas_rhino.select_curves()
        keys = DiagramHelper.identify_vertices_on_curves(diagram, guids)
        DiagramHelper.highlight_vertices(diagram, keys)
        return keys

    @staticmethod
    def select_edges_on_curves(diagram):
        rs.UnselectAllObjects()
        guids = compas_rhino.select_curves()
        keys = DiagramHelper.identify_edges_on_curves(diagram, guids)
        DiagramHelper.highlight_edges(diagram, keys)
        return keys

    @staticmethod
    def select_continuous_edges(diagram):
        rs.UnselectAllObjects()
        keys = DiagramHelper.select_edges(diagram)
        if not keys:
            return
        keys = [diagram.get_continuous_edges(key) for key in keys]
        keys = list(set(list(flatten(keys))))
        DiagramHelper.highlight_edges(diagram, keys)
        return keys

    @staticmethod
    def select_parallel_edges(diagram):
        rs.UnselectAllObjects()
        keys = DiagramHelper.select_edges(diagram)
        if not keys:
            return
        keys = [diagram.get_parallel_edges(key) for key in keys]
        keys = list(set(list(flatten(keys))))
        DiagramHelper.highlight_edges(diagram, keys)
        return keys

    @staticmethod
    def identify_vertices_on_points(diagram, guids):
        gkey_key = diagram.gkey_key()
        keys = []
        for guid in guids:
            point = RhinoPoint.from_guid(guid)
            gkey = geometric_key(point.xyz)
            if gkey in gkey_key:
                key = gkey_key[gkey]
                keys.append(key)
        return keys

    @staticmethod
    def identify_vertices_on_curve(diagram, guid):
        gkey_key = diagram.gkey_key()
        keys = []
        curve = RhinoCurve.from_guid(guid)
        for key in diagram.vertices():
            xyz = diagram.vertex_coordinates(key)
            closest = curve.closest_point(xyz)
            gkey = geometric_key(closest)
            if gkey in gkey_key:
                if key == gkey_key[gkey]:
                    keys.append(key)
        return keys

    @staticmethod
    def identify_vertices_on_curves(diagram, guids):
        gkey_key = diagram.gkey_key()
        keys = []
        for guid in guids:
            curve = RhinoCurve.from_guid(guid)
            for key in diagram.vertices():
                xyz = diagram.vertex_coordinates(key)
                closest = curve.closest_point(xyz)
                gkey = geometric_key(closest)
                if gkey in gkey_key:
                    if key == gkey_key[gkey]:
                        keys.append(key)
        return keys

    @staticmethod
    def identify_edges_on_curves(diagram, guids):
        edges = []
        for guid in guids:
            keys = DiagramHelper.identify_vertices_on_curve(diagram, guid)
            if keys:
                vertices = set(keys)
                for u, v in diagram.edges():
                    if u in vertices and v in vertices:
                        edges.append((u, v))
        return edges

    @staticmethod
    def move(diagram):
        color  = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
        origin = {key: diagram.vertex_coordinates(key) for key in diagram.vertices()}
        vertex = {key: diagram.vertex_coordinates(key) for key in diagram.vertices()}
        edges  = list(diagram.edges())
        start  = compas_rhino.pick_point('Point to move from?')

        if not start:
            return False

        def OnDynamicDraw(sender, e):
            current = list(e.CurrentPoint)
            vec = [current[i] - start[i] for i in range(3)]

            for key in vertex:
                vertex[key] = [origin[key][i] + vec[i] for i in range(3)]

            for u, v in iter(edges):
                sp = vertex[u]
                ep = vertex[v]
                sp = Point3d(*sp)
                ep = Point3d(*ep)
                e.Display.DrawDottedLine(sp, ep, color)

        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Point to move to?')
        gp.DynamicDraw += OnDynamicDraw

        gp.Get()

        if gp.CommandResult() == Rhino.Commands.Result.Success:
            end = list(gp.Point())
            vec = [end[i] - start[i] for i in range(3)]

            for key, attr in diagram.vertices(True):
                attr['x'] += vec[0]
                attr['y'] += vec[1]
                attr['z'] += vec[2]

            return True
        return False

