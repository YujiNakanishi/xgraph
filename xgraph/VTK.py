import numpy as np
import xgraph

class UnstructuredGrid(xgraph.coreVTK):
    def __init__(self,
                 name : str = "unstructured_grid",
                 node_pos : np.ndarray = None,
                 cells_info = None,
                 ):
        super().__init__(name, node_pos)
        self.cells_info = [] if cells_info is None else cells_info #<list:dict> dict -> {"type":int, "node_id":list:(n, )}
    
    @property
    def data_type(self):
        return "UNSTRUCTURED_GRID"
    @property
    def num_cell(self):
        return len(self.cells_info)
    @property
    def size_cell(self):
        size = 0
        for cell in self.cells_info:
            size += 1 + len(cell["node_id"])
        return size
    
    def write_geo(self, file):
        file.write("POINTS {0} float\n".format(self.num_node))
        for pos in self.node_pos:
            file.write("{0} {1} {2}\n".format(pos[0], pos[1], pos[2]))

        cells_string = []
        cells_type_string = []
        for cell in self.cells_info:
            s = str(len(cell["node_id"]))
            for i in range(len(cell["node_id"])):
                s += " {0}".format(cell["node_id"][i])
            cells_string.append(s+"\n")
            cells_type_string.append("{0}\n".format(cell["type"]))
        file.write("CELLS {0} {1}\n".format(self.num_cell, self.size_cell))
        for cell_string in cells_string:
            file.write(cell_string)
        file.write("CELL_TYPES {0}\n".format(self.num_cell))
        for cell_type_string in cells_type_string:
            file.write(cell_type_string)


class PointCloud(UnstructuredGrid):
    def __init__(self, name : str = "point_cloud", node_pos : np.ndarray = None):
        super().__init__(name, node_pos)
        self.cells_info = [{"type" : 1, "node_id" : [i+1]} for i in range(self.num_node)]

class Graph(UnstructuredGrid):
    def __init__(self, 
                 name : str = "point_cloud", 
                 node_pos : np.ndarray = None, 
                 edge_index : np.ndarray = None, #<np:int:(2, edge_num)> COO format
                 ):
        super().__init__(name, node_pos)
        self.cells_info = [{"type" : 3, "node_id" : [ei[0], ei[1]]} for ei in edge_index.T]