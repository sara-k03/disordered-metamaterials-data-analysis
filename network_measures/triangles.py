import math
import os
import sys

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 -- registers the 3D projection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from networkx.algorithms.cluster import all_triangles

# dataset_imports.py lives at the repo root, one level up from this file's directory --
# add it to sys.path so this script works whether it's run from the repo root or imported
# from anywhere else.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from dataset_imports import *
from plot_specific_modulus import specific_modulus

OUTPUT_ROOT = "triangle_plots"

# Same marker/color-by-a-value convention as plot_specific_modulus.plot_specific_modulus.
MARKERS = ['o', 's', '^', 'D', 'P', 'X']
COLORS = ["#C1C187", '#d4e09b', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']

_AXIS_VECTORS = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}

# Adjacency .npy rows include near-zero-weight entries for struts that weren't actually
# built (e.g. the a=0.001 Voronoi sample has 1449/3416 rows with weight < 0.01 -- keeping
# them creates phantom triangles that don't exist in the physical lattice). Drop any row
# at or below this weight before building the graph.
MIN_EDGE_WEIGHT = 0.01


def _resolve_tesselation(tesselation):
    """Accept either a letter code ("V") or a full name ("Voronoi"), case-insensitive."""
    tesselation = str(tesselation).strip()
    if tesselation.upper() in TESSELATION_NAMES:
        return tesselation.upper()

    for letter, name in TESSELATION_NAMES.items():
        if tesselation.lower() == name.lower():
            return letter

    raise ValueError(
        f"Unknown tesselation '{tesselation}'; expected one of {list(TESSELATION_NAMES)} "
        f"or {list(TESSELATION_NAMES.values())}"
    )


def _npy_dataset(tesselation, a):
    """Look up the NPY_DATASETS entry (adjacency_file + point_cloud_file) for a tesselation/a-value."""
    letter = _resolve_tesselation(tesselation)
    for dataset in NPY_DATASETS[letter]:
        if math.isclose(dataset["a"], a, rel_tol=1e-9, abs_tol=1e-9):
            return dataset

    available = sorted(d["a"] for d in NPY_DATASETS[letter])
    raise ValueError(f"No npy dataset for tesselation '{tesselation}' at a={a}; available a-values: {available}")


def _resolve_axis(axis):
    """Accept "x"/"y"/"z" (aliases like "x-hat" also work, case-insensitive) or an explicit 3-vector."""
    if isinstance(axis, str):
        key = axis.strip().lower()
        for suffix in ("-hat", "_hat", "hat", "̂"):
            if key.endswith(suffix):
                key = key[: -len(suffix)]
                break
        if key not in _AXIS_VECTORS:
            raise ValueError(f"Unknown axis '{axis}'; expected 'x', 'y', 'z', or a 3-vector")
        return np.array(_AXIS_VECTORS[key])

    vec = np.asarray(axis, dtype=float)
    norm = np.linalg.norm(vec)
    if norm == 0:
        raise ValueError("axis vector must be nonzero")
    return vec / norm


def _load_graph(adjacency_file, min_weight=MIN_EDGE_WEIGHT):
    """
    Build a weighted networkx Graph from a saved adjacency .npy file, dropping any row
    with weight <= min_weight (an unbuilt/phantom strut -- see MIN_EDGE_WEIGHT).
    """
    edges = np.load(adjacency_file)
    node_i = edges[:, 0].astype(int)
    node_j = edges[:, 1].astype(int)
    weights = edges[:, 2]

    keep = weights > min_weight
    G = nx.Graph()
    G.add_weighted_edges_from(zip(node_i[keep], node_j[keep], weights[keep]))
    return G


def count_triangles(file):
    """
    Return the number of triangles in the graph stored in an adjacency .npy file
    (rows of [node_i, node_j, weight]). Rows with weight <= MIN_EDGE_WEIGHT are treated
    as struts that weren't actually built and are excluded.
    """
    return len(list(all_triangles(_load_graph(file))))


def _triangle_axis_weight(u, v, w, coords, axis_vec):
    """
    Weight for one triangle (u, v, w): the component of its area-weighted normal vector
    that's perpendicular to `axis_vec`, i.e. |normal x axis_vec| = |normal| * sin(theta)
    where theta is the angle between the normal and the axis.

    Each triangle's normal is the cross product of two of its edges, so its magnitude is
    twice the triangle's area -- bigger triangles contribute more. Weighting by the
    perpendicular component (rather than the parallel/dot-product component) means a
    triangle contributes most when its normal is perpendicular to the axis (theta=90,
    weight=|normal|) and nothing when its normal is parallel to the axis (theta=0,
    weight=0), i.e. triangles whose face contains the axis direction dominate.
    """
    normal = np.cross(coords[v] - coords[u], coords[w] - coords[u])
    return np.linalg.norm(np.cross(normal, axis_vec))


def count_weighted_triangles(tesselation, a, axis):
    """
    Sum, over every triangle in a tesselation sample's graph, the perpendicular
    (axis-normal) component of the triangle's area-weighted normal vector -- see
    _triangle_axis_weight. Triangles whose normal is perpendicular to `axis` (i.e. the
    triangle's face contains the axis direction) contribute the most.

    tesselation - a tesselation letter ("C", "D", "G", "V") or name ("Centroidal", ...)
    a           - disorder value, e.g. 0.25 (must have a saved adjacency/point-cloud pair)
    axis        - "x", "y", or "z" (aliases like "x-hat" also accepted), or an explicit 3-vector
    """
    dataset = _npy_dataset(tesselation, a)
    axis_vec = _resolve_axis(axis)

    G = _load_graph(dataset["adjacency_file"])
    coords = np.load(dataset["point_cloud_file"])

    return sum(_triangle_axis_weight(u, v, w, coords, axis_vec) for u, v, w in all_triangles(G))


def plot_tesselation(tesselation, ax=None, save_path=None, show=True, start_zero=True):
    """
    Graphs number of triangles vs. a-value (Kick Size, alpha) for every saved sample of a
    tesselation, using the same marker/color-by-a-value convention as plot_specific_modulus.

    tesselation - a tesselation letter ("C", "D", "G", "V") or name ("Centroidal", ...)
    ax          - optional existing matplotlib Axes to draw on; a new figure/axes is made if omitted
    save_path   - optional path to save the figure to
    show        - whether to display the figure (plt.show())
    start_zero  - if True, the y-axis starts at 0
    """
    letter = _resolve_tesselation(tesselation)
    title = TESSELATION_NAMES[letter]

    if ax is None:
        _, ax = plt.subplots()

    # a-values and adjacency-file paths come straight from dataset_imports.py's
    # NPY_DATASETS, same spirit as plot_specific_modulus.plot_specific_modulus reading
    # TESSELATION_DATASETS.
    datasets = sorted(NPY_DATASETS[letter], key=lambda d: d["a"])
    all_a_values = [d["a"] for d in datasets]
    marker_for_a = {a: MARKERS[i % len(MARKERS)] for i, a in enumerate(all_a_values)}
    color_for_a = {a: COLORS[i % len(COLORS)] for i, a in enumerate(all_a_values)}

    # Collect one legend handle per a-value
    legend_handles = {}

    for dataset in datasets:
        a = dataset["a"]
        n_triangles = count_triangles(dataset["adjacency_file"])
        handle = ax.scatter(
            a,
            n_triangles,
            marker=marker_for_a[a],
            color=color_for_a[a],
            s=120,
            label=f"a={a}",
        )
        legend_handles[a] = handle

    ax.set_xlabel("Kick Size, α", fontsize=12)
    ax.set_ylabel("Number of Triangles", fontsize=12)
    ax.set_xticks(all_a_values)
    ax.legend([legend_handles[a] for a in all_a_values], [f"a={a}" for a in all_a_values])

    ax.tick_params(axis='both', labelsize=12)
    ax.set_title(f"{title} — Number of Triangles vs Disorder")
    if start_zero:
        ax.set_ylim(bottom=0)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)

    if show:
        plt.show()

    return ax


def plot_weighted_tesselation(tesselation, ax=None, save_path=None, show=True, start_zero=True):
    """
    Graphs weighted-triangle count (see count_weighted_triangles) vs. a-value (Kick Size,
    alpha) for every saved sample of a tesselation, plotting all three of x-hat, y-hat, and
    z-hat for each a-value. Color distinguishes a-value (same convention as plot_tesselation);
    marker shape distinguishes axis -- a literal "X", "Y", or "Z" glyph.

    tesselation - a tesselation letter ("C", "D", "G", "V") or name ("Centroidal", ...)
    ax          - optional existing matplotlib Axes to draw on; a new figure/axes is made if omitted
    save_path   - optional path to save the figure to
    show        - whether to display the figure (plt.show())
    start_zero  - if True, the y-axis starts at 0
    """
    letter = _resolve_tesselation(tesselation)
    title = TESSELATION_NAMES[letter]

    if ax is None:
        _, ax = plt.subplots()

    datasets = sorted(NPY_DATASETS[letter], key=lambda d: d["a"])
    all_a_values = [d["a"] for d in datasets]
    color_for_a = {a: COLORS[i % len(COLORS)] for i, a in enumerate(all_a_values)}
    marker_for_axis = {"x": "$X$", "y": "$Y$", "z": "$Z$"}

    # Collect one legend handle per a-value (color), not per axis (the X/Y/Z glyphs are
    # self-explanatory).
    legend_handles = {}

    for dataset in datasets:
        a = dataset["a"]
        for axis in ("x", "y", "z"):
            weighted_count = count_weighted_triangles(letter, a, axis)
            handle = ax.scatter(
                a,
                weighted_count,
                marker=marker_for_axis[axis],
                color=color_for_a[a],
                s=120,
                label=f"a={a}",
            )
            legend_handles.setdefault(a, handle)

    ax.set_xlabel("Kick Size, α", fontsize=12)
    ax.set_ylabel("Weighted Triangle Count", fontsize=12)
    ax.set_xticks(all_a_values)
    ax.legend([legend_handles[a] for a in all_a_values], [f"a={a}" for a in all_a_values])

    ax.tick_params(axis='both', labelsize=12)
    ax.set_title(f"{title} — Weighted Triangle Count vs Disorder")
    if start_zero:
        ax.set_ylim(bottom=0)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)

    if show:
        plt.show()

    return ax


def plot_triangles_vs_modulus(tesselation, cycle=CYCLE, ax=None, save_path=None, show=True, start_zero=True):
    """
    Graphs number of triangles (x-axis) vs. specific modulus (y-axis, from
    plot_specific_modulus.specific_modulus) for every saved sample of a tesselation. Marker
    and color are keyed by a-value, same convention as plot_tesselation. Since specific
    modulus data can have multiple orientations per a-value (see specific_modulus), every
    orientation is plotted -- points sharing an a-value share the same x (triangle count)
    but may differ in y (that orientation's specific modulus).

    tesselation - a tesselation letter ("C", "D", "G", "V") or name ("Centroidal", ...)
    cycle       - which loading cycle to isolate (passed through to specific_modulus)
    ax          - optional existing matplotlib Axes to draw on; a new figure/axes is made if omitted
    save_path   - optional path to save the figure to
    show        - whether to display the figure (plt.show())
    start_zero  - if True, the y-axis starts at 0
    """
    letter = _resolve_tesselation(tesselation)
    title = TESSELATION_NAMES[letter]

    if ax is None:
        _, ax = plt.subplots()

    datasets = sorted(NPY_DATASETS[letter], key=lambda d: d["a"])
    all_a_values = [d["a"] for d in datasets]
    marker_for_a = {a: MARKERS[i % len(MARKERS)] for i, a in enumerate(all_a_values)}
    color_for_a = {a: COLORS[i % len(COLORS)] for i, a in enumerate(all_a_values)}
    triangles_for_a = {d["a"]: count_triangles(d["adjacency_file"]) for d in datasets}

    modulus_data = specific_modulus(letter, cycle=cycle)

    # Collect one legend handle per a-value
    legend_handles = {}

    for i in range(len(modulus_data["a_values"])):
        a = modulus_data["a_values"][i]
        handle = ax.errorbar(
            triangles_for_a[a],
            modulus_data["specific_modulus"][i],
            yerr=modulus_data["specific_modulus_err"][i],
            fmt=marker_for_a[a],
            color=color_for_a[a],
            markersize=12,
            capsize=8,
            elinewidth=2,
            label=f"a={a}",
        )
        legend_handles[a] = handle

    ax.set_xlabel("Number of Triangles", fontsize=12)
    ax.set_ylabel(r"Specific Modulus, $\mathrm{N\ mm^{-1}\ kg^{-1}}$", fontsize=12)
    ax.legend([legend_handles[a] for a in all_a_values], [f"a={a}" for a in all_a_values])

    ax.tick_params(axis='both', labelsize=12)
    ax.set_title(f"{title} Cycle {cycle} — Specific Modulus vs Number of Triangles")
    if start_zero:
        ax.set_ylim(bottom=0)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)

    if show:
        plt.show()

    return ax


def plot_weighted_triangles_vs_modulus(tesselation, cycle=CYCLE, ax=None, save_path=None, show=True, start_zero=True):
    """
    Graphs weighted-triangle count (x-axis, see count_weighted_triangles) vs. specific
    modulus (y-axis, from plot_specific_modulus.specific_modulus) for every saved sample of
    a tesselation, plotting all three of x-hat, y-hat, and z-hat for each a-value. Color
    distinguishes a-value (same convention as plot_tesselation); marker shape distinguishes
    axis -- a literal "X", "Y", or "Z" glyph. Every specific-modulus orientation is plotted
    (see plot_triangles_vs_modulus), so a given a-value/axis pair may appear at the same x
    with multiple y's.

    tesselation - a tesselation letter ("C", "D", "G", "V") or name ("Centroidal", ...)
    cycle       - which loading cycle to isolate (passed through to specific_modulus)
    ax          - optional existing matplotlib Axes to draw on; a new figure/axes is made if omitted
    save_path   - optional path to save the figure to
    show        - whether to display the figure (plt.show())
    start_zero  - if True, the y-axis starts at 0
    """
    letter = _resolve_tesselation(tesselation)
    title = TESSELATION_NAMES[letter]

    if ax is None:
        _, ax = plt.subplots()

    datasets = sorted(NPY_DATASETS[letter], key=lambda d: d["a"])
    all_a_values = [d["a"] for d in datasets]
    color_for_a = {a: COLORS[i % len(COLORS)] for i, a in enumerate(all_a_values)}
    marker_for_axis = {"x": "$X$", "y": "$Y$", "z": "$Z$"}
    weighted_for_a = {
        a: {axis: count_weighted_triangles(letter, a, axis) for axis in ("x", "y", "z")}
        for a in all_a_values
    }

    modulus_data = specific_modulus(letter, cycle=cycle)

    # Collect one legend handle per a-value (color), not per axis (the X/Y/Z glyphs are
    # self-explanatory).
    legend_handles = {}

    for i in range(len(modulus_data["a_values"])):
        a = modulus_data["a_values"][i]
        for axis in ("x", "y", "z"):
            handle = ax.errorbar(
                weighted_for_a[a][axis],
                modulus_data["specific_modulus"][i],
                yerr=modulus_data["specific_modulus_err"][i],
                marker=marker_for_axis[axis],
                linestyle='none',
                color=color_for_a[a],
                markersize=12,
                capsize=8,
                elinewidth=2,
                label=f"a={a}",
            )
            legend_handles.setdefault(a, handle)

    ax.set_xlabel("Weighted Triangle Count", fontsize=12)
    ax.set_ylabel(r"Specific Modulus, $\mathrm{N\ mm^{-1}\ kg^{-1}}$", fontsize=12)
    ax.legend([legend_handles[a] for a in all_a_values], [f"a={a}" for a in all_a_values])

    ax.tick_params(axis='both', labelsize=12)
    ax.set_title(f"{title} Cycle {cycle} — Specific Modulus vs Weighted Triangle Count")
    if start_zero:
        ax.set_ylim(bottom=0)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)

    if show:
        plt.show()

    return ax


def visualize_weighted_triangles(tesselation, a, axis, output_dir=None, show=True):
    """
    Draws one tesselation sample's 3D network (nodes + edges) with every triangle face
    filled in, shaded darker the more perpendicular its normal is to `axis` (see
    count_weighted_triangles). The plot title also reports the total weighted-triangle
    count for `axis`, computed via count_weighted_triangles.

    tesselation - a tesselation letter ("C", "D", "G", "V") or name ("Centroidal", ...)
    a           - disorder value, e.g. 0.25 (must have a saved adjacency/point-cloud pair)
    axis        - "x", "y", or "z" (aliases like "x-hat" also accepted), or an explicit 3-vector
    output_dir  - optional directory to save the figure (.png/.pdf) to; None to skip saving
    show        - whether to display the figure (plt.show())
    """
    letter = _resolve_tesselation(tesselation)
    title = TESSELATION_NAMES[letter]
    dataset = _npy_dataset(letter, a)
    axis_vec = _resolve_axis(axis)
    weighted_count = count_weighted_triangles(letter, a, axis)

    G = _load_graph(dataset["adjacency_file"])
    coords = np.load(dataset["point_cloud_file"])

    triangles = list(all_triangles(G))
    weights = [_triangle_axis_weight(u, v, w, coords, axis_vec) for u, v, w in triangles]

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")

    # Edges (no node markers -- they just obscured the triangle faces)
    for u, v in G.edges():
        ax.plot(
            [coords[u, 0], coords[v, 0]],
            [coords[u, 1], coords[v, 1]],
            [coords[u, 2], coords[v, 2]],
            color="gray", alpha=0.4, linewidth=1, zorder=1,
        )

    # Triangle faces -- darker red means the normal is more perpendicular to the axis
    if triangles:
        cmap = plt.colormaps["Reds"]
        norm = mcolors.Normalize(vmin=min(weights), vmax=max(weights))
        face_colors = [cmap(norm(w)) for w in weights]
        polys = [[coords[u], coords[v], coords[w]] for u, v, w in triangles]

        collection = Poly3DCollection(polys, facecolors=face_colors, edgecolor="k", linewidths=0.3, alpha=0.85)
        ax.add_collection3d(collection)

        mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array([])
        plt.colorbar(mappable, ax=ax, label=f"|normal × {axis}| (area-weighted)", shrink=0.6)

    # Reference arrow showing the axis direction, placed just outside the point cloud
    bounds_min = coords.min(axis=0)
    bounds_max = coords.max(axis=0)
    extent = (bounds_max - bounds_min).max()
    arrow_origin = bounds_min - 0.15 * extent
    arrow_length = 0.4 * extent
    ax.quiver(
        *arrow_origin, *axis_vec,
        length=arrow_length, color="tab:blue", linewidth=3, arrow_length_ratio=0.3,
    )
    axis_label = axis if isinstance(axis, str) else np.array2string(axis_vec, precision=2)
    ax.text(*(arrow_origin + axis_vec * arrow_length * 1.15), axis_label, color="tab:blue", fontsize=12, weight="bold")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(
        f"{title} Tesselation, a={a:g} — Triangles Weighted Along {axis}\n"
        f"Weighted Triangle Count: {weighted_count:.3g}"
    )
    plt.tight_layout()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.join(output_dir, f"{title}-Weighted-Triangles-{axis}-a{a:g}")
        plt.savefig(f"{base}.png")
        plt.savefig(f"{base}.pdf")

    if show:
        plt.show()

    return fig, ax


if __name__ == "__main__":
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    """This is to generate the plot for weighted triangles"""
    for letter in TESSELATION_NAMES:
        title = TESSELATION_NAMES[letter]
        plot_weighted_tesselation(
            letter,
            save_path=os.path.join(OUTPUT_ROOT, f"{title}-Weighted-Triangles-vs-Disorder.png"),
            show=False,
        )
        plt.close("all")

    """This is for the visualization plots, no plot has been made for this yet"""
    # visualize_weighted_triangles("centroidal", 1, "x", output_dir=None, show=True)

    """This is to generate the plot for all triangles"""
    for letter in TESSELATION_NAMES:
        title = TESSELATION_NAMES[letter]
        plot_tesselation(
            letter,
            save_path=os.path.join(OUTPUT_ROOT, f"{title}-Triangles-vs-Disorder.png"),
            show=False,
        )
        plt.close("all")

    """This is to generate the plot for number of triangles vs specific modulus"""
    for letter in TESSELATION_NAMES:
        title = TESSELATION_NAMES[letter]
        plot_triangles_vs_modulus(
            letter,
            save_path=os.path.join(OUTPUT_ROOT, f"{title}-Triangles-vs-Specific-Modulus.png"),
            show=False,
        )
        plt.close("all")

    """This is to generate the plot for weighted triangles vs specific modulus"""
    for letter in TESSELATION_NAMES:
        title = TESSELATION_NAMES[letter]
        plot_weighted_triangles_vs_modulus(
            letter,
            save_path=os.path.join(OUTPUT_ROOT, f"{title}-Weighted-Triangles-vs-Specific-Modulus.png"),
            show=False,
        )
        plt.close("all")
