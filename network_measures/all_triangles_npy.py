import numpy as np
import networkx as nx
from networkx.algorithms.cluster import all_triangles

edges = np.load("adjacency_matrices/PC216V3D_216_3D-box_Z3_V_URL_adj_1.00.npy")
node_i = edges[:, 0].astype(int)
node_j = edges[:, 1].astype(int)
weights = edges[:, 2]

G = nx.Graph()
G.add_weighted_edges_from(zip(node_i, node_j, weights))

triangles = list(all_triangles(G))
print(f"Number of triangles: {len(triangles)}")