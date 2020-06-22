from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__all__ = ['SceneObject', 'Scene']


ITEM_OBJECT = {}
ITEM_ARTIST = {}


class SceneObject(object):

    def __init__(self, item):
        self.item = item
        self.artist = ITEM_ARTIST[type(item)](item)

    @staticmethod
    def register(itemtype, objecttype, artisttype):
        ITEM_OBJECT[itemtype] = objecttype
        ITEM_ARTIST[itemtype] = artisttype

    def draw(self):
        self.artist.draw()


class Scene(object):

    def __init__(self):
        self.objects = {}

    def add(self, item, name=None, layer=None, settings=None):
        self.objects[name] = ITEM_OBJECT[type(item)](item, layer=layer, settings=settings)

    def update(self):
        for name in self.objects:
            self.objects[name].draw()

    def clear(self):
        for name in self.objects:
            self.objects[name].clear()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
