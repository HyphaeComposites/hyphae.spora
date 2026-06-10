"""
scripts/export_results.py
--------------------------
Export experiment results from Supabase to local CSV and Parquet files.
Parquet is a compressed binary format that loads much faster than CSV
for large datasets — useful when you have thousands of descriptor rows.

Usage:
    python scripts/export_results.py --output-dir data/exports/
    # or via Makefile:
    make export
"""

import click
import pandas as pd
from pathlib import Path
from spora.db.queries import get_latest_runs, get_run_summary


@click.command()
@click.option("--output-dir", default="data/exports", help="Directory to write export files into")
@click.option("--label", default=None, help="Export a specific run by label. Omit to export all completed runs.")
@click.option("--format", "fmt", default="both", type=click.Choice(["csv", "parquet", "both"]), help="Output file format")
def export(output_dir, label, fmt):
    """Export SPORA experiment results to local files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"→ Exporting results to {output_path}/...")

    if label:
        labels = [label]
    else:
        click.echo("→ Fetching list of completed runs...")
        runs_df = get_latest_runs(n=100)
        if runs_df.empty:
            click.echo("  No completed runs found. Run make run-degradation first.")
            return
        labels = runs_df["label"].tolist()
        click.echo(f"  Found {len(labels)} completed run(s).")

    for run_label in labels:
        click.echo(f"  Exporting: {run_label}...")
        df = get_run_summary(run_label)

        if fmt in ("csv", "both"):
            csv_path = output_path / f"{run_label}_summary.csv"
            df.to_csv(csv_path, index=False)
            click.echo(f"    ✓ CSV → {csv_path}")

        if fmt in ("parquet", "both"):
            parquet_path = output_path / f"{run_label}_summary.parquet"
            df.to_parquet(parquet_path, index=False)
            click.echo(f"    ✓ Parquet → {parquet_path}")

    click.echo(f"\n✓ Export complete. Files are in {output_path}/")


if __name__ == "__main__":
    export()
