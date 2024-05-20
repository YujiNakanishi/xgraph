import numpy as np
from xgraph import MSH

class msh:
    def __init__(self):
        pass
    def read(self, filename):
        with open(filename, "r") as file:
            MSH.read(self, file)