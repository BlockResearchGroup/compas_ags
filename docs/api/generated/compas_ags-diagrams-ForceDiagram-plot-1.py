import compas
from compas.datastructures import Network

network = Network.from_obj(compas.get('lines.obj'))

network.plot()