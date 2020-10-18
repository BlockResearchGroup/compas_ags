import os
import json

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '../data/forms/howe_modified.ags')

with open(FILE, 'r') as f:
    data = json.load(f)

    form = FormDiagram.from_data(data['data']['form'])
    force = ForceDiagram.from_data(data['data']['force'])
    form.dual = force
    force.dual = form

print(form.edgedata)

print(len(list(form.edges())))
print(len(list(force.edges())))
