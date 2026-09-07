import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# --- File paths for each a-value ---
files = {
    0.25: "adjacency_matrices/PC216V3D_216_3D-box_Z3_V_URL_adj_0.25.npy",
    0.50: "adjacency_matrices/PC216V3D_216_3D-box_Z3_V_URL_adj_0.50.npy",
    0.75: "adjacency_matrices/PC216V3Dcl_216_3D-box_Z3_V_URL_adj_0.75.npy",
    1.00: "adjacency_matrices/PC216V3D_216_3D-box_Z3_V_URL_adj_1.00.npy",
}

colors = ['#C1C187', '#a1dab4', '#41b6c4', '#2c7fb8']
a_values = list(files.keys())

# --- Compute node BC for each a-value ---
all_bc = {}

for a, filepath in files.items():
    edges = np.load(filepath)
    node_i = edges[:, 0].astype(int)
    node_j = edges[:, 1].astype(int)
    weights = edges[:, 2]

    G = nx.Graph()
    G.add_weighted_edges_from(zip(node_i, node_j, weights))

    betweenness = nx.betweenness_centrality(G, normalized=True, weight='weight')
    all_bc[a] = np.array(list(betweenness.values()))

# --- Shared bin edges across all a-values ---
global_min = min(bc.min() for bc in all_bc.values())
global_max = max(bc.max() for bc in all_bc.values())
bin_edges = np.linspace(global_min, global_max, 51)

# --- Plot ---
fig, ax = plt.subplots(figsize=(8, 5))

for a, color in zip(a_values, colors):
    bc_values = all_bc[a]

    # no zeros
    # for i in len(bc_values):
    #     if bc_values[i] == 0:
            

    counts, _ = np.histogram(bc_values, bins=bin_edges)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    probability = counts / counts.sum()

    ax.plot(bin_centers, probability, color=color,
            linewidth=1.5, label=f"α={a:.2f}")

ax.set_xlim(global_min, global_max)
# ax.set_yscale('log')
ax.set_xlabel("Node Betweenness Centrality", fontsize=12)
ax.set_ylabel("Probability", fontsize=12)
# ax.set_ylabel("Log(Probability)", fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(fontsize=11)
plt.tick_params(axis='both', labelsize=12)
plt.title("Node Betweenness Centrality Distribution by Kick Factor, α", fontsize=13)
plt.tight_layout()
plt.savefig("Node-BC-Histogram.png", dpi=300)
plt.savefig("Node-BC-Histogram.pdf")
# plt.savefig("Node-BC-Histogram-Log.png", dpi=300)
# plt.savefig("Node-BC-Histogram-Log.pdf")
plt.show()