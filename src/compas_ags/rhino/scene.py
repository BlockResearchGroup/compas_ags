from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from uuid import uuid4

import compas_rhino
from compas_ags.rhino.diagramobject import DiagramObject


__all__ = ['Scene']


class Scene(object):

    def __init__(self):
        self.objects = {}

    def add(self, item, name=None, layer=None, visible=None, settings=None):
        guid = uuid4()
        obj = DiagramObject.build(item, scene=self, name=name, layer=layer, visible=visible, settings=settings)
        self.objects[guid] = obj
        return guid

    def find(self, guid):
        if guid in self.objects:
            return self.objects[guid]

    def clear(self):
        for guid in self.objects:
            self.objects[guid].clear()

    def update(self):
        for guid in self.objects:
            self.objects[guid].draw()
        compas_rhino.rs.EnableRedraw(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
