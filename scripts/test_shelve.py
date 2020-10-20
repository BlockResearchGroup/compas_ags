import os
import pickle
import shelve

from compas.geometry import Point

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '../data/debugging/truss.obj')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)

s = pickle.dumps(form)

db = shelve.open('test', 'n', 2, False)

db['form'] = form.data

print(db['form'])

p = Point(0, 0, 0)

db['p'] = p.data

print(db['p'])
