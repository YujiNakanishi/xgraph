import numpy as np
import gmsh
import sys

def read(msh, file):
    lines = file.read().split("$")[3:]
    lines = [lines[i].split("\n") for i in range(0, len(lines), 2)]
    for line in lines:
        if line[0] == "PhysicalNames":
            num = int(line[1])
            msh.physval = []
            for i in range(2, num+2):
                l = line[i].split()
                msh.physval.append({"dim" : int(l[0]), "tag" : int(l[1]), "name" : l[2][1:-1]})
            
        elif line[0] == "Nodes":
            num = int(line[1])
            nodes = []
            for i in range(2, num + 2):
                l = line[i].split()
                x = float(l[1])
                y = float(l[2])
                z = float(l[3])
                nodes.append(np.array([x, y, z]))
            msh.nodes = np.stack(nodes, axis = 0)
        
        elif line[0] == "Elements":
            num = int(line[1])
            print(num)
            sys.exit()




    # print(a[0][:-1] == "$MeshFormat")
    # def get_physValue():
    #     physValue = []
    #     num = int(file.readline()[:-1])
    #     for _ in range(num):
    #         l = file.readline()[:-1].split()
    #         physValue.append({"dim" : int(l[0]), "tag" : int(l[1]), "name" : l[2][1:-1]})
        
    #     return physValue
    
    # def get_Nodes():
    #     num = int(file.readline()[:-1])
    #     node = []
    #     sys.exit()
    #     # for _ in num:




    # ##### emit $MeshFormat
    # while True:
    #     if file.readline()[:-1] == "$EndMeshFormat":
    #         break
    
    # while True:
    #     ### read until EOF
    #     line = file.readline()[:-1]
    #     if not line:
    #         break
    #     if line == "$PhysicalNames":
    #         msh.physValue = get_physValue()
    #     elif line == "$Nodes":
    #         node = get_Nodes()



"""
write msh graph data which doesn't contain node data.
"""
def write_graph(
        node_pos : np.ndarray,
        edge_index : np.ndarray,
        filename : str,
        ):
    
    num_node = len(node_pos)
    element_num = edge_index.shape[1]
    with open(filename, "w") as file:
        file.write("$MeshFormat\n")
        file.write("2.2 0 8\n")
        file.write("$EndMeshFormat\n")
        file.write("$Nodes\n")
        file.write("{0}\n".format(num_node))
        for i in range(num_node):
            x, y, z = node_pos[i][0], node_pos[i][1], node_pos[i][2]
            file.write("{0} {1} {2} {3}\n".format(i+1, x, y, z))
        file.write("$EndNodes\n")
        file.write("$Elements\n")
        file.write("{0}\n".format(element_num))
        for i in range(element_num):
            e1, e2 = edge_index[0][i]+1, edge_index[1][i]+1
            file.write("{0} 1 2 0 1 {1} {2}\n".format(i+1, e1, e2))
        file.write("$EndElements")