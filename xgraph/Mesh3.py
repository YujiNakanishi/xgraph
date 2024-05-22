import numpy as np
from xgraph.core import stl
from xgraph.core import mesh3
import sys

def import_from_stls(stls):
    nodes = np.concatenate([stl.triangles.reshape((-1, 3)) for stl in stls], axis = 0)
    nodes = np.unique(nodes, axis = 0)

    triangles = []

    for stl in stls:
        name = stl.name

        for triangle in stl.triangles:
            vertex1 = triangle[0]
            vertex2 = triangle[1]
            vertex3 = triangle[2]
            
            e_tag = [0, 0, 0]
            count = 0
            i = 0
            while True:
                if count == 3:
                    break
                if np.allclose(nodes[i], vertex1, atol = 1e-3):
                    e_tag[0] = i
                    count += 1
                elif np.allclose(nodes[i], vertex2, atol = 1e-3):
                    e_tag[1] = i
                    count += 1
                elif np.allclose(nodes[i], vertex3, atol = 1e-3):
                    e_tag[2] = i
                    count += 1
                
                i += 1
            
            triangles.append({"name" : name, "id" : e_tag})
    
    return mesh3(nodes, triangles)