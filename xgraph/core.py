import numpy as np
from xgraph import MSH

class stl:
    def __init__(self, facet_normal = None, triangles = None, name = None):
        self.facet_normal = facet_normal
        self.triangles = triangles
        self.name = name

    def __len__(self):
        return len(self.facet_normal)