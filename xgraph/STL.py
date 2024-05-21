import numpy as np
from xgraph.core import stl
import sys

def read_ASCII(filename):
    Info = []
    stls = []
    with open(filename, "r") as file:
        for f in file:
            f = f[:-1].split(" ")
            f = [s for s in f if s != ""]

            if "solid" in f:
                Info.append({"name" : f[-1], "facet_normals" : [], "vertice" : []})
            
            elif f[0] == "facet":
                x, y, z = float(f[2]), float(f[3]), float(f[4])
                Info[-1]["facet_normals"].append(np.array([x, y, z]))
            
            elif f[0] == "vertex":
                x, y, z = float(f[1]), float(f[2]), float(f[3])
                Info[-1]["vertice"].append(np.array([x, y, z]))
            else:
                pass

        for info in Info:
            facet_normals = np.stack(info["facet_normals"])
            triangles = np.stack(info["vertice"]).reshape((-1,3,3))
            stls.append(stl(facet_normals, triangles, info["name"]))
    
    return tuple(stls)

def write_ASCII(stl, filename):
    with open(filename, "w") as file:
        file.write("solid {}\n".format(stl.name))

        for i in range(len(stl)):
            fn = stl.facet_normal[i]
            v1, v2, v3 = stl.triangles[i][0], stl.triangles[i][1], stl.triangles[i][2]
            file.write("facet normal {0} {1} {2}\n".format(fn[0], fn[1], fn[2]))
            file.write("outer loop\n")
            file.write("vertex {0} {1} {2}\n".format(v1[0], v1[1], v1[2]))
            file.write("vertex {0} {1} {2}\n".format(v2[0], v2[1], v2[2]))
            file.write("vertex {0} {1} {2}\n".format(v3[0], v3[1], v3[2]))
            file.write("endloop\n")
            file.write("endfacet\n")
        
        file.write("endsolid {}".format(stl.name))