"""
spora/ovito_pipeline/renderer.py
----------------------------------
Renders molecular conformers into publication-quality images
using matplotlib and Hyphae brand colors.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from spora.ovito_pipeline.loader import load_conformer_series

BG_COLOR = "#0D1117"
ACCENT_TEAL = "#6DCFB2"
NAVY = "#1B2340"
SLATE = "#4A5568"
WHITE = "#FFFFFF"


def _render_molecule_ax(ax, xyz_data, title, step_label=""):
    ax.set_facecolor(BG_COLOR)
    atoms = xyz_data["atoms"]
    if not atoms:
        ax.text(0.5, 0.5, "No atoms", color=WHITE, ha="center", va="center", transform=ax.transAxes)
        return
    xs = [a["x"] for a in atoms]
    ys = [a["y"] for a in atoms]
    colors = [a["color"] for a in atoms]
    sizes = [a["size"] for a in atoms]
    for i, a1 in enumerate(atoms):
        for j, a2 in enumerate(atoms):
            if j <= i:
                continue
            dist = np.sqrt((a1["x"]-a2["x"])**2 + (a1["y"]-a2["y"])**2)
            if dist < 1.8:
                ax.plot([a1["x"], a2["x"]], [a1["y"], a2["y"]], color="#3A4A6A", linewidth=0.8, zorder=1)
    ax.scatter(xs, ys, c=colors, s=sizes, zorder=2, edgecolors="none")
    ax.set_title(title, color=ACCENT_TEAL, fontsize=11, fontweight="bold", pad=8)
    if step_label:
        ax.text(0.98, 0.02, step_label, color=SLATE, fontsize=7, ha="right", va="bottom", transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    for spine in ax.spines.values():
        spine.set_edgecolor(SLATE)
        spine.set_linewidth(0.5)


def render_single(conformer_dir, output_path, run_label):
    series = load_conformer_series(conformer_dir)
    if not series:
        raise ValueError(f"No XYZ files found in {conformer_dir}")
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    fig.patch.set_facecolor(BG_COLOR)
    _render_molecule_ax(ax, series[-1], run_label, step_label=f"Step {len(series)-1}")
    fig.text(0.99, 0.01, "SPORA — Hyphae Composites", color=SLATE, fontsize=6, ha="right", va="bottom")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR, edgecolor="none")
    plt.close()
    return output_path


def render_comparison(conformer_dirs, labels, output_path):
    n = len(conformer_dirs)
    fig = plt.figure(figsize=(6 * n, 7))
    fig.patch.set_facecolor(BG_COLOR)
    gs = gridspec.GridSpec(2, n, height_ratios=[8, 1], hspace=0.15)
    for i, (cdir, label) in enumerate(zip(conformer_dirs, labels)):
        ax = fig.add_subplot(gs[0, i])
        series = load_conformer_series(cdir)
        if series:
            _render_molecule_ax(ax, series[-1], label, step_label=f"Final state — {len(series)-1} steps")
        else:
            ax.set_facecolor(BG_COLOR)
            ax.text(0.5, 0.5, "No data", color=WHITE, ha="center", va="center", transform=ax.transAxes)
    ax_footer = fig.add_subplot(gs[1, :])
    ax_footer.set_facecolor(NAVY)
    ax_footer.text(0.5, 0.5, "SPORA Computational Pipeline  •  Hyphae Composites  •  Confidential",
                   color=ACCENT_TEAL, fontsize=9, ha="center", va="center",
                   transform=ax_footer.transAxes, fontweight="bold")
    ax_footer.set_xticks([])
    ax_footer.set_yticks([])
    for spine in ax_footer.spines.values():
        spine.set_visible(False)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR, edgecolor="none")
    plt.close()
    return output_path


def render_timelapse(conformer_dir, output_dir, run_label):
    series = load_conformer_series(conformer_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_paths = []
    for i, xyz_data in enumerate(series):
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        fig.patch.set_facecolor(BG_COLOR)
        _render_molecule_ax(ax, xyz_data, f"{run_label} — Step {i}", step_label=f"{i}/{len(series)-1}")
        fig.text(0.99, 0.01, "SPORA — Hyphae Composites", color=SLATE, fontsize=6, ha="right", va="bottom")
        out = os.path.join(output_dir, f"step_{i:03d}.png")
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG_COLOR, edgecolor="none")
        plt.close()
        output_paths.append(out)
    return output_paths
