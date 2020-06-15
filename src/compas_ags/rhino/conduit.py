from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.conduits import Conduit

try:
    import Rhino
    import scriptcontext as sc
    
    from Rhino.Geometry import Point3d
    from Rhino.Geometry import Line

    from System.Drawing.Color import FromArgb

    white       = FromArgb(255, 255, 255)

except ImportError:
    compas.raise_if_ironpython()


__all__ = ['ForceConduit', 
            'FormConduit'
        ]


class ForceConduit(Conduit):
    """Conduit for mesh algorithms.

    """

    def __init__(self, force, face_colordict={}, **kwargs):
        super(ForceConduit, self).__init__(**kwargs)

        self.force           = force
        self.face_colordict = face_colordict

    def DrawForeground(self, e):
        _conduit_mesh_edges(self.force, e)

        if self.face_colordict:
            for fkey in self.face_colordict:
                color  = FromArgb(*self.face_colordict[fkey])
                points = self.force.face_coordinates(fkey)
                points.append(points[0])
                points  = [Point3d(*pt) for pt in points]
                e.Display.DrawPolygon(points, color, filled=True)


class FormConduit(Conduit):
    """Conduit for mesh algorithms.

    """

    def __init__(self, form, face_colordict={}, **kwargs):
        super(FormConduit, self).__init__(**kwargs)

        self.form           = form
        self.face_colordict = face_colordict

    def DrawForeground(self, e):
        _conduit_mesh_edges(self.form, e)

        if self.face_colordict:
            for fkey in self.face_colordict:
                color  = FromArgb(*self.face_colordict[fkey])
                points = self.form.face_coordinates(fkey)
                points.append(points[0])
                points  = [Point3d(*pt) for pt in points]
                e.Display.DrawPolygon(points, color, filled=True)


def _conduit_mesh_edges(mesh, e):
    for u, v in mesh.edges():
        sp = mesh.vertex_coordinates(u)
        ep = mesh.vertex_coordinates(v)
        e.Display.DrawPoint(Point3d(*sp), 0, 4, white)
        e.Display.DrawPoint(Point3d(*ep), 0, 4, white)
        e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), white, 1)