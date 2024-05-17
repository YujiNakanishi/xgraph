"""
point cloudに対しr以下の距離のpoint同士をつなげ、エッジを作成。ただし次数がmax_num_neghborsを超えないように抑える。
pointとedge_indexをmshファイルに書き込み、Gmsh上でグラフを可視化。
"""

import torch
from torch_geometric.nn import radius_graph
import xgraph

points = torch.rand(100, 3, dtype = torch.float) #node position
edge_index = radius_graph(points, r = 1., max_num_neighbors=10)
points = points.numpy()
edge_index = edge_index.numpy()
xgraph.MSH.write_graph(points, edge_index, "radius_graph_test.msh")