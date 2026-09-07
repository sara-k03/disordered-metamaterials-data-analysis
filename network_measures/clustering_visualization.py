import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Build graph
edges = np.load("adjacency_matrices/PC216V3D_216_3D-box_Z3_V_URL_adj_1.00.npy")
G = nx.Graph()
G.add_weighted_edges_from(zip(edges[:,0].astype(int), edges[:,1].astype(int), edges[:,2]))

# Load coordinates — shape (N, 3)
coords = np.load("point_clouds/PC216V3D_216_3D-box_Z3_V_URL_xy_1.00.npy")  
xs, ys, zs = coords[:, 0], coords[:, 1], coords[:, 2]

# Per-node clustering coefficients
clustering = nx.clustering(G)
node_colors = [clustering[n] for n in G.nodes()]

fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(xs, ys, zs, c=node_colors, cmap='viridis', s=60, zorder=5)

# Draw edges
for u, v in G.edges():
    ax.plot([coords[u, 0], coords[v, 0]],
            [coords[u, 1], coords[v, 1]],
            [coords[u, 2], coords[v, 2]],
            color='black', alpha=0.5, linewidth=1)

plt.colorbar(sc, ax=ax, label="Clustering Coefficient", shrink=0.6)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.title("Node Clustering Coefficient, a=1.00")
plt.tight_layout()
plt.savefig("visualizations/Node-Clustering-Visualization-1.00.png")
plt.savefig("visualizations/Node-Clustering-Visualization-1.00.pdf")