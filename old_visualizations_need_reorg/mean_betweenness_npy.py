import numpy as np
import networkx as nx

edges = np.load("adjacency_matrices/PC216V3Dcl_216_3D-box_Z3_V_URL_adj_0.75.npy")
node_i = edges[:, 0].astype(int)
node_j = edges[:, 1].astype(int)
weights = edges[:, 2]

G = nx.Graph()
G.add_weighted_edges_from(zip(node_i, node_j, weights))

betweenness = nx.betweenness_centrality(G, normalized=True, weight='weight')
mean_betweenness = np.mean(list(betweenness.values()))
print(f"Mean betweenness centrality: {mean_betweenness}")