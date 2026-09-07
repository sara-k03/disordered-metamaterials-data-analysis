
import os

import matplotlib.pyplot as plt

import data_extraction.cycle_separation as cycle_separation
import data_extraction.fits as fits
from data_extraction.plot_cycle import plot_cycle
from dataset_imports import CYCLE, TESSELATION_DATASETS, TESSELATION_NAMES

OUTPUT_ROOT = "cycle_plots"


def _format_a_tag(a):
    """
    Reproduce the old scripts' filename tags from an a-value:
    0.125 -> "125", 0.5 -> "5", 1.0 -> "1", ~0 -> "0".
    """
    if a < 0.01:
        return "0"
    s = f"{a:g}"
    return s[2:] if s.startswith("0.") else s.replace(".", "")


def plot_cycle_fits(tesselation, cycle=CYCLE, orientation=None, output_dir=None):
    
    if tesselation not in TESSELATION_DATASETS:
        raise ValueError(f"Unknown tesselation '{tesselation}'; expected one of {list(TESSELATION_DATASETS)}")

    datasets = TESSELATION_DATASETS[tesselation]
    if orientation is not None:
        datasets = [d for d in datasets if d["orientation"] == orientation]
        if not datasets:
            raise ValueError(f"No '{tesselation}' datasets found for orientation '{orientation}'")

    multiple_orientations = len({d["orientation"] for d in datasets}) > 1

    if output_dir is None:
        output_dir = os.path.join(OUTPUT_ROOT, TESSELATION_NAMES[tesselation])
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    for ds in datasets:
        tag = _format_a_tag(ds["a"])
        key = f"{tag}_{ds['orientation']}" if multiple_orientations else tag

        # --- Load raw data ---------------------------------------------------
        comp_x_raw, comp_y_raw, rel_x_raw, rel_y_raw = cycle_separation.cycle_separation(
            ds["file"], n=cycle, foam_load=ds["load"]
        )

        # --- Shift raw data to origin (same shift the fit functions apply) --
        comp_x_shifted, comp_y_shifted, rel_x_shifted, rel_y_shifted, _, _ = fits.shift_raw(
            comp_x_raw, comp_y_raw, rel_x_raw, rel_y_raw
        )

        # --- Linear fit --------------------------------------------------------
        (lm, lm_err,
         lf_x_up, lf_y_up, lf_comp_eq,
         lf_x_down, lf_y_down, lf_rel_eq) = fits.linear_fit(comp_x_raw, comp_y_raw, rel_x_raw, rel_y_raw)

        # --- Power fit -----------------------------------------------------
        (n_comp, n_rel,
         pf_x_up, pf_y_up, pf_comp_eq,
         pf_x_down, pf_y_down, pf_rel_eq,
         n_comp_err, n_rel_err) = fits.power_fit(comp_x_raw, comp_y_raw, rel_x_raw, rel_y_raw)

        # Stash anything you might want later (e.g. for a modulus-vs-disorder plot)
        results[key] = {
            "a": ds["a"],
            "orientation": ds["orientation"],
            "linear_modulus": lm,
            "linear_modulus_err": lm_err,
            "n_compression": n_comp,
            "n_release": n_rel,
        }

        # --- Plot ------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 6))

        # Raw data
        plot_cycle(comp_x_shifted, comp_y_shifted, "Displacement (mm)", "Force (N)", "Compression (raw)", "Black", ax, "None", "--")
        plot_cycle(rel_x_shifted, rel_y_shifted, "Displacement (mm)", "Force (N)", "Release (raw)", "Gray", ax, "None", "--")

        # Power fits
        plot_cycle(pf_x_up, pf_y_up, "Displacement (mm)", "Force (N)", f"Power fit compression: {pf_comp_eq}", "Red", ax, "None", "-")
        plot_cycle(pf_x_down, pf_y_down, "Displacement (mm)", "Force (N)", f"Power fit release: {pf_rel_eq}", "Orange", ax, "None", "-")

        # Linear fit
        plot_cycle(lf_x_down, lf_y_down, "Displacement (mm)", "Force (N)", f"Linear fit release: {lf_rel_eq}", "Cyan", ax, "None", "-")

        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

        ax.set_title(f"{ds['title']}, Cycle {cycle}")
        ax.tick_params(axis='both', labelsize=12)
        plt.tight_layout()

        out_base = os.path.join(
            output_dir,
            f"{TESSELATION_NAMES[tesselation]}-a{tag}-Orientation{ds['orientation']}-Cycle{cycle}",
        )
        plt.savefig(f"{out_base}.png")
        plt.close(fig)

        print(f"Saved plot for {ds['title']} -> {out_base}.png")

    return results


# if __name__ == "__main__":
#     for tesselation in TESSELATION_DATASETS:
#         plot_cycle_fits(tesselation)
