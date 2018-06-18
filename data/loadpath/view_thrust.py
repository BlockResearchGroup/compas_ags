
from compas_ags.diagrams import FormDiagram
from compas_rhino.helpers import NetworkArtist


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


form = FormDiagram.from_json('F:/compas_ags/data/loadpath/diagonal.json')
print(form.attributes['loadpath'])

artist = NetworkArtist(form, layer='Thrust')
artist.clear_layer()
artist.draw_edges(keys=form.edges_where({'is_symmetry': False}), color='ee0000')
