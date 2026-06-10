"""
scripts/run_ovito.py
---------------------
CLI entry point for the OVITO molecular visualisation pipeline.
Reads XYZ coordinate files produced by run_degradation.py and
renders them into images or animations.

Usage:
    python scripts/run_ovito.py \\
        --run-label "pla_hydro_60c_2pct" \\
        --mode comparison \\
        --output-dir visualizations/pla_hydro_60c_2pct/

    # or via Makefile:
    make run-ovito ARGS="--run-label pla_hydro_60c_2pct --mode comparison"

Modes:
    single      — one image of the final degraded state
    comparison  — side-by-side: pristine vs degraded vs masterbatch-recovered
    timelapse   — animated MP4 across all time steps

TODO: implement the rendering logic in spora/ovito_pipeline/renderer.py
      once the RDKit pipeline is producing XYZ conformer files.
"""

import click
from pathlib import Path


@click.command()
@click.option("--run-label",   required=True, help="Label of the completed degradation run to visualise")
@click.option("--mode",        required=True, type=click.Choice(["single", "comparison", "timelapse"]), help="Render mode")
@click.option("--output-dir",  required=True, help="Directory to write rendered images/videos into")
def run_ovito(run_label, mode, output_dir):
    """Run the OVITO molecular visualisation pipeline for a completed experiment."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    conformer_dir = Path("data/processed") / run_label / "conformers"

    click.echo(f"\n→ OVITO visualisation pipeline")
    click.echo(f"  Run label : {run_label}")
    click.echo(f"  Mode      : {mode}")
    click.echo(f"  Input     : {conformer_dir}")
    click.echo(f"  Output    : {output_path}")

    if not conformer_dir.exists():
        click.echo(f"\n  ⚠  Conformer directory not found: {conformer_dir}")
        click.echo(f"     Run the degradation pipeline first: make run-degradation")
        return

    # TODO: call spora/ovito_pipeline/renderer.py once implemented
    click.echo("\n  TODO: OVITO rendering not yet implemented.")
    click.echo("  Next step: implement spora/ovito_pipeline/renderer.py")


if __name__ == "__main__":
    run_ovito()
