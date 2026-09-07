import matplotlib.pyplot as plt
import data_extraction.cycle_separation
import data_extraction.fits
from dataset_imports import CYCLE, TESSELATION_DATASETS, TESSELATION_NAMES


def specific_modulus(tesselation, cycle=CYCLE, orientation=None):
    """
    Computes linear modulus, mass, and specific modulus (linear modulus / mass) for every
    dataset belonging to a tesselation, sorted by a-value.

    tesselation - one of "G", "V", "D", "C"
    cycle       - which loading cycle to isolate (passed through to cycle_separation)
    orientation - optional filter, e.g. "O" or "1" or "N". Leave as None to include every orientation
                  present for that tesselation.
    Returns a dict of parallel lists (all sorted together by a-value):
        a_values, orientation, title, linear_modulus, linear_modulus_err,
        mass, specific_modulus, specific_modulus_err
    """
    if tesselation not in TESSELATION_DATASETS:
        raise ValueError(f"Unknown tesselation '{tesselation}'; expected one of {list(TESSELATION_DATASETS)}")

    datasets = TESSELATION_DATASETS[tesselation]
    if orientation is not None:
        datasets = [d for d in datasets if d["orientation"] == orientation]
        if not datasets:
            raise ValueError(f"No '{tesselation}' datasets found for orientation '{orientation}'")

    datasets = sorted(datasets, key=lambda d: (d["a"], d["orientation"]))

    results = {
        "a_values": [],
        "orientation": [],
        "title": [],
        "linear_modulus": [],
        "linear_modulus_err": [],
        "mass": [],
        "specific_modulus": [],
        "specific_modulus_err": [],
    }

    for dataset in datasets:
        x_up, y_up, x_down, y_down = data_extraction.cycle_separation.cycle_separation(
            dataset["file"], n=cycle, foam_load=dataset["load"]
        )
        linear_modulus, linear_modulus_err, *_ = data_extraction.fits.linear_fit(
            x_up, y_up, x_down, y_down
        )

        results["a_values"].append(dataset["a"])
        results["orientation"].append(dataset["orientation"])
        results["title"].append(dataset["title"])
        results["linear_modulus"].append(linear_modulus)
        results["linear_modulus_err"].append(linear_modulus_err)
        results["mass"].append(dataset["mass"])
        results["specific_modulus"].append(linear_modulus / dataset["mass"])
        results["specific_modulus_err"].append(linear_modulus_err / dataset["mass"])

    return results


def plot_specific_modulus(tesselation, cycle=CYCLE, ax=None, save_path=None):
    """
    Graphs specific modulus vs. a-value (Kick Size, alpha) for a single tesselation.

    tesselation - one of "G", "V", "D", "C"
    cycle       - which loading cycle to isolate
    ax          - optional existing matplotlib Axes to draw on; a new figure/axes is made if omitted
    save_path   - optional path to save the figure to
    """
    if tesselation not in TESSELATION_DATASETS:
        raise ValueError(f"Unknown tesselation '{tesselation}'; expected one of {list(TESSELATION_DATASETS)}")

    if ax is None:
        _, ax = plt.subplots()

    markers = ['o', 's', '^', 'D', 'P', 'X']
    colors = ["#C1C187", '#d4e09b', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']

    orientations = sorted({d["orientation"] for d in TESSELATION_DATASETS[tesselation]})

    # Marker and color are distinguished by a-value
    all_a_values = sorted({d["a"] for d in TESSELATION_DATASETS[tesselation]})
    marker_for_a = {a: markers[i % len(markers)] for i, a in enumerate(all_a_values)}
    color_for_a = {a: colors[i % len(colors)] for i, a in enumerate(all_a_values)}

    # Collect one legend handle per a-value
    legend_handles = {}

    for orientation in orientations:
        data = specific_modulus(tesselation, cycle=cycle, orientation=orientation)

        for i in range(len(data["a_values"])):
            a = data["a_values"][i]
            handle = ax.errorbar(
                a,
                data["specific_modulus"][i],
                yerr=data["specific_modulus_err"][i],
                fmt=marker_for_a[a],
                color=color_for_a[a],
                markersize=12,
                capsize=8,
                elinewidth=2,
                label=f"a={a}",
            )
            legend_handles[a] = handle

    ax.set_xlabel("Kick Size, α", fontsize=12)
    ax.set_ylabel(r"Specific Modulus, $\mathrm{N\ mm^{-1}\ kg^{-1}}$", fontsize=12)
    ax.set_xticks(all_a_values)
    ax.set_ylim(bottom=0, top=0.50)
    ax.legend([legend_handles[a] for a in all_a_values], [f"a={a}" for a in all_a_values])

    ax.tick_params(axis='both', labelsize=12)
    ax.set_title(f"{TESSELATION_NAMES[tesselation]} Cycle {cycle} — Specific Modulus vs Disorder")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)

    return ax


# if __name__ == "__main__":
#     for tesselation in TESSELATION_DATASETS:
#         plot_specific_modulus(
#             tesselation,
#             save_path=f"{TESSELATION_NAMES[tesselation]}-Specific-Modulus-vs-Disorder-Cycle{CYCLE}.png",
#         )
