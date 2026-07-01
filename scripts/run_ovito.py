"""
scripts/run_ovito.py
---------------------
CLI entry point for the SPORA molecular visualisation pipeline.
"""

import click
from pathlib import Path
from spora.ovito_pipeline.renderer import render_single, render_comparison, render_timelapse


@click.command()
@click.option("--run-label",    required=True, help="Label of the completed degradation run to visualise")
@click.option("--mode",         required=True, type=click.Choice(["single", "comparison", "timelapse"]), help="Render mode")
@click.option("--output-dir",   required=True, help="Directory to write rendered images into")
@click.option("--compare-with", default=None, multiple=True, help="Additional run labels for comparison mode")
def run_ovito(run_label, mode, output_dir, compare_with):
    """Run the SPORA molecular visualisation pipeline for a completed experiment."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    conformer_dir = Path("data/processed") / run_label / "conformers"

    click.echo(f"\n→ SPORA visualisation pipeline")
    click.echo(f"  Run label : {run_label}")
    click.echo(f"  Mode      : {mode}")
    click.echo(f"  Input     : {conformer_dir}")
    click.echo(f"  Output    : {output_path}")

    if not conformer_dir.exists():
        click.echo(f"\n  ⚠  Conformer directory not found: {conformer_dir}")
        click.echo(f"     Run the degradation pipeline first.")
        return

    if mode == "single":
        out = str(output_path / f"{run_label}.png")
        render_single(str(conformer_dir), out, run_label)
        click.echo(f"\n✓ Rendered: {out}")

    elif mode == "comparison":
        all_labels = [run_label] + list(compare_with)
        all_dirs = [str(Path("data/processed") / lbl / "conformers") for lbl in all_labels]
        out = str(output_path / "comparison.png")
        render_comparison(all_dirs, all_labels, out)
        click.echo(f"\n✓ Comparison rendered: {out}")

    elif mode == "timelapse":
        frames = render_timelapse(str(conformer_dir), str(output_path / "frames"), run_label)
        click.echo(f"\n✓ Timelapse: {len(frames)} frames in {output_path}/frames/")


if __name__ == "__main__":
    run_ovito()
