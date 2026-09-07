import numpy as np
from collections import Counter

edges = np.load("adjacency_matrices/PC216V3D_216_3D-box_Z3_V_URL_adj_0.50.npy")

node_i = edges[:, 0].astype(int)
node_j = edges[:, 1].astype(int)

# Count degree of each node
degree_count = Counter(np.concatenate([node_i, node_j]))

degrees = np.array(list(degree_count.values()))
degrees = degrees[degrees > 1] # Filter nodes on the points

print(f"Unique nodes:   {len(degrees)}")
print(f"Total edges:    {len(edges)}")
print(f"Average degree: {degrees.mean():.4f}")