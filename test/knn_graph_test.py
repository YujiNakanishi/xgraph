"""
point cloudの各pointに対しKNNを実施し、エッジを作成。
pointとedge_indexをmshファイルに書き込み、Gmsh上でグラフを可視化。
"""

import torch
from torch_geometric.nn import knn_graph
import xgraph

points = torch.rand(100, 3, dtype = torch.float) #node position
edge_index = knn_graph(points, 6)
points = points.numpy()
edge_index = edge_index.numpy()
xgraph.MSH.write_graph(points, edge_index, "knn_graph_test.msh")