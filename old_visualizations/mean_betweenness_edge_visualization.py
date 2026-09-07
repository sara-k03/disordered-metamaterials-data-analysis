import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d.art3d import Line3DCollection

# --- Load data ---
edges = np.load("adjacency_matrices/PC216V3D_216_3D-box_Z3_V_URL_adj_1.00.npy")
positions = np.load("point_clouds/PC216V3D_216_3D-box_Z3_V_URL_xy_1.00.npy") 

node_i = edges[:, 0].astype(int)
node_j = edges[:, 1].astype(int)
weights = edges[:, 2]

G = nx.Graph()
G.add_weighted_edges_from(zip(node_i, node_j, weights))

# --- Compute edge betweenness centrality ---
edge_betweenness = nx.edge_betweenness_centrality(G, normalized=True, weight='weight')

# --- Build segments and BC values in the same order ---
segments = []
bc_values = []

for (i, j), bc in edge_betweenness.items():
    segments.append([positions[i], positions[j]])
    bc_values.append(bc)

segments = np.array(segments)   # shape (E, 2, 3)
bc_values = np.array(bc_values)

# --- Normalise and map to colormap ---
norm = mcolors.Normalize(vmin=bc_values.min(), vmax=bc_values.max())
cmap = cm.viridis

# --- Plot ---
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

lc = Line3DCollection(segments, cmap=cmap, norm=norm, linewidth=0.5)
lc.set_array(bc_values)
ax.add_collection3d(lc)

# Fit axes to the node positions
ax.set_xlim(positions[:, 0].min(), positions[:, 0].max())
ax.set_ylim(positions[:, 1].min(), positions[:, 1].max())
ax.set_zlim(positions[:, 2].min(), positions[:, 2].max())

# Match the dark aesthetic of your reference image
ax.set_facecolor('#0a0a1e')
fig.patch.set_facecolor('#0a0a1e')
ax.grid(False)
ax.set_axis_off()

cbar = fig.colorbar(lc, ax=ax, pad=0.05, shrink=0.6)
cbar.set_label("Edge BC", color='white')
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

plt.title("Edge Betweenness Centrality, a=1.00", color='white')
plt.tight_layout()
plt.savefig("Edge-Betweenness-Centrality-a1.00-Visualization.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.savefig("Edge-Betweenness-Centrality-a1.00-Visualization.pdf", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())

# plt.show()