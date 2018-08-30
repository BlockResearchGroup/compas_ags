import compas
from compas.datastructures import Network
from compas.plotters import NetworkPlotter

network = Network.from_obj(compas.get('lines.obj'))

u, v = network.get_any_edge()

a = network.split_edge(u, v)

lines = []
for u, v in network.edges():
    lines.append({
        'start': network.vertex_coordinates(u, 'xy'),
        'end'  : network.vertex_coordinates(v, 'xy'),
        'arrow': 'end',
        'width': 4.0,
        'color': '#00ff00'
    })

plotter = NetworkPlotter(network)

plotter.draw_lines(lines)

plotter.draw_vertices(
    radius=0.2,
    text={key: key for key in network.vertices()},
    facecolor={key: '#ff0000' for key in (a,)}
)
plotter.draw_edges()

plotter.show()