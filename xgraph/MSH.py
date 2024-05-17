import numpy as np
import gmsh

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