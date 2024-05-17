import numpy as np

class coreVTK:
    def __init__(self,
                 name : str = "xgraph",
                 node_pos : np.ndarray = None,
                 ):
        self.node_pos = node_pos #<np:float:(num_node, 3)>
        self.name = name
    @property
    def __version__(self):
        return "2.0"
    @property
    def data_type(self):
        raise NotImplementedError
    @property
    def num_node(self):
        return 0 if self.node_pos is None else len(self.node_pos)
    
    def write_head(self, file):
        file.write("# vtk DataFile Version {0}\n".format(self.__version__))
        file.write("{0}\n".format(self.name))
        file.write("ASCII\n")
        file.write("DATASET {}\n".format(self.data_type))
    
    def write_geo(self, file):
        raise NotImplementedError
    def write(self, filename):
        with open(filename, "w") as file:
            self.write_head(file)
            self.write_geo(file)