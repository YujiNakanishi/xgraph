import numpy as np
import xgraph
import pyvista
import sys

"""
pyvista.UnstructuredGridから隣接行列を計算。
"""
def get_AdjacencyMatrix(usgrid):
    def read_9(cells):
        node_start = []
        node_end = []
        for cell in cells:
            node_start.append(cell)
            node_end.append(np.roll(cell, -1))
            node_start.append(np.roll(cell, -1))
            node_end.append(cell)
        node_start = np.concatenate(node_start)
        node_end = np.concatenate(node_end)

        edge_index = np.stack((node_start, node_end), axis = 0)
        edge_index = np.unique(edge_index, axis = 1)

        return edge_index

    cells_dict = usgrid.cells_dict
    A = []
    for t, cells in cells_dict.items():
        if t == 9:
            A.append(read_9(cells))
        else:
            print("t = {}".format(t))
            raise NotImplementedError
    A = np.concatenate(A, axis = 1).astype(np.int)

    return A