from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from System.Collections.Generic import List
from System.Drawing.Color import FromArgb
from Rhino.Geometry import Point3d
from Rhino.Geometry import Line

from compas_rhino.conduits import BaseConduit
from compas_rhino.ui import Mouse

from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors


__all__ = [
    'FormDiagramVertexInspector',
    # 'FormDiagramEdgeInspector',
]


class FormDiagramInspector(BaseConduit):

    @property
    def form_vertex_xyz(self):
        return self._form_vertex_xyz

    @form_vertex_xyz.setter
    def form_vertex_xyz(self, vertex_xyz):
        self._form_vertex_xyz = vertex_xyz

    @property
    def force_vertex_xyz(self):
        return self._force_vertex_xyz

    @force_vertex_xyz.setter
    def force_vertex_xyz(self, vertex_xyz):
        self._force_vertex_xyz = vertex_xyz

    def enable(self):
        """Enable the conduit."""
        self.mouse.Enabled = True
        self.Enabled = True

    def disable(self):
        """Disable the conduit."""
        self.mouse.Enabled = False
        self.Enabled = False


# class FormDiagramEdgeInspector(FormDiagramInspector):
#     """Inspect diagram topology at the vertices.

#     Parameters
#     ----------
#     mesh: :class:`compas_ags.diagrams.ForceDiagram`
#     tol: float, optional
#     dotcolor: rgb-tuple, optional
#     textcolor: rgb-tuple, optional
#     linecolor: rgb-tuple, optional
#     """

#     def __init__(self, force, tol=0.1, dotcolor=None, textcolor=None, linecolor=None, **kwargs):
#         super(FormDiagramEdgeInspector, self).__init__(**kwargs)
#         dotcolor = dotcolor or (255, 255, 0)
#         textcolor = textcolor or (0, 0, 0)
#         linecolor = linecolor or (255, 255, 0)
#         self._form_vertex_xyz = None
#         self._force_vertex_xyz = None
#         self.form = force.dual
#         self.force = force
#         self.tol = tol
#         self.dotcolor = FromArgb(*dotcolor)
#         self.textcolor = FromArgb(*textcolor)
#         self.linecolor = FromArgb(*linecolor)
#         self.mouse = Mouse(self)
#         self.force_edges = list(self.force.ordered_edges(self.form))
#         self.form_edges = list(self.form.edges())


class FormDiagramVertexInspector(FormDiagramInspector):
    """Inspect diagram topology at the vertices.

    Parameters
    ----------
    mesh: :class:`compas_ags.diagrams.ForceDiagram`
    tol: float, optional
    dotcolor: rgb-tuple, optional
    textcolor: rgb-tuple, optional
    linecolor: rgb-tuple, optional
    """

    def __init__(self, form, tol=0.1, dotcolor=None, textcolor=None, linecolor=None, **kwargs):
        super(FormDiagramVertexInspector, self).__init__(**kwargs)
        dotcolor = dotcolor or (255, 255, 0)
        textcolor = textcolor or (0, 0, 0)
        linecolor = linecolor or (255, 255, 0)
        self._form_vertex_xyz = None
        self._force_vertex_xyz = None
        self.form = form
        self.force = form.dual
        self.tol = tol
        self.dotcolor = FromArgb(*dotcolor)
        self.textcolor = FromArgb(*textcolor)
        self.linecolor = FromArgb(*linecolor)
        self.mouse = Mouse(self)
        self.form_edges = list(self.form.edges())
        self.force_edges = list(self.force.ordered_edges(self.form))
        self.form_vertex_edges = {}
        for edge in self.form_edges:
            u, v = edge
            if u not in self.form_vertex_edges:
                self.form_vertex_edges[u] = []
            self.form_vertex_edges[u].append(edge)
            if v not in self.form_vertex_edges:
                self.form_vertex_edges[v] = []
            self.form_vertex_edges[v].append(edge)
        self.force_face_edges = {}
        for face in self.force.faces():
            self.force_face_edges[face] = [
                edge if self.force.has_edge(edge) else (edge[1], edge[0])
                for edge in self.force.face_halfedges(face)]

    def DrawForeground(self, e):
        draw_dot = e.Display.DrawDot
        draw_arrows = e.Display.DrawArrows
        a = self.mouse.p1
        b = self.mouse.p2
        ab = subtract_vectors(b, a)
        Lab = length_vector(ab)
        if not Lab:
            return
        for index, vertex in enumerate(self.form_vertex_xyz):
            c = self.form_vertex_xyz[vertex]
            D = length_vector(cross_vectors(subtract_vectors(a, c), subtract_vectors(b, c)))
            if D / Lab < self.tol:
                point = Point3d(*c)
                draw_dot(point, str(index), self.dotcolor, self.textcolor)
                lines = List[Line](len(self.form_vertex_edges[vertex]))
                for u, v in self.form_vertex_edges[vertex]:
                    lines.Add(Line(Point3d(* self.form_vertex_xyz[u]), Point3d(* self.form_vertex_xyz[v])))
                draw_arrows(lines, self.linecolor)
                lines = List[Line](len(self.force_face_edges[vertex]))
                for u, v in self.force_face_edges[vertex]:
                    lines.Add(Line(Point3d(* self.force_vertex_xyz[u]), Point3d(* self.force_vertex_xyz[v])))
                draw_arrows(lines, self.linecolor)
                break
