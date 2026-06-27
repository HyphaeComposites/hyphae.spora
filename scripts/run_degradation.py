"""
scripts/run_degradation.py
--------------------------
CLI entry point for running a SPORA degradation experiment.
Calls into the spora/ package — all real logic lives there.

Usage:
    python scripts/run_degradation.py \\
        --polymer PLA \\
        --mechanism hydrolysis \\
        --temperature 60 \\
        --time-steps 10 \\
        --masterbatch-concentration 0.02 \\
        --output-label "pla_hydro_60c_2pct"
"""

import subprocess
import sys
import click
from rdkit import rdBase

from spora.db.queries import get_polymer, get_mechanism, insert_experiment
from spora.models.experiment import ExperimentSpec
from spora.rdkit_pipeline.smiles_builder import build_polymer_smiles
from spora.rdkit_pipeline.degradation import apply_degradation
from spora.rdkit_pipeline.descriptors import compute_descriptors
from spora.db.queries import insert_descriptors_batch
from rdkit import Chem


def get_git_sha() -> str:
    """Return the current git commit SHA for reproducibility tracking."""
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()
    except Exception:
        return "unknown"


@click.command()
@click.option("--polymer",                  required=True,  help="Polymer name — e.g. PLA, PETG, ABS")
@click.option("--mechanism",                required=True,  help="Degradation mechanism code — e.g. hydrolysis, thermal")
@click.option("--temperature",              required=True,  type=float, help="Temperature in °C")
@click.option("--time-steps",               required=True,  type=int,   help="Number of degradation steps to simulate")
@click.option("--masterbatch-concentration",default=None,   type=float, help="Masterbatch weight fraction (e.g. 0.02 = 2%)")
@click.option("--output-label",             required=True,  help="Unique name for this run — e.g. pla_hydro_60c_2pct")
@click.option("--run-by",                   default="mariana", help="Your name or initials")
@click.option("--chain-length",             default=50,     type=int,   help="Number of repeat units in starting polymer")
def run(polymer, mechanism, temperature, time_steps, masterbatch_concentration, output_label, run_by, chain_length):
    """Run a SPORA degradation experiment and write results to Supabase."""

    click.echo(f"\n→ Starting SPORA run: {output_label}")
    click.echo(f"  Polymer: {polymer}  |  Mechanism: {mechanism}  |  Temp: {temperature}°C  |  Steps: {time_steps}")

    # 1 — Look up polymer in database
    click.echo("→ Fetching polymer from database...")
    polymer_record = get_polymer(polymer)

    # 2 — Look up mechanism in database
    click.echo("→ Fetching mechanism from database...")
    mechanism_record = get_mechanism(mechanism)

    # 3 — Create experiment row in database
    click.echo("→ Creating experiment record...")
    experiment_id = insert_experiment({
        "label":            output_label,
        "polymer_id":       polymer_record["id"],
        "mechanism_id":     mechanism_record["id"],
        "temperature_c":    temperature,
        "time_steps":       time_steps,
        "masterbatch_pct":  masterbatch_concentration,
        "chain_length_n":   chain_length,
        "rdkit_version":    rdBase.rdkitVersion,
        "git_sha":          get_git_sha(),
        "run_by":           run_by,
        "notes":            None,
    })
    click.echo(f"  Experiment ID: {experiment_id}")

    # 3 — Build starting polymer molecule
    click.echo("→ Building polymer SMILES...")
    polymer_smiles = build_polymer_smiles(polymer_record["smiles_monomer"], chain_length)
    mol = Chem.MolFromSmiles(polymer_smiles)

    # 4 — Run degradation steps and collect descriptors
    click.echo(f"→ Running {time_steps} degradation steps...")
    conditions = {"temperature_c": temperature, "masterbatch_pct": masterbatch_concentration}
    fragments = [mol]

    for step in range(time_steps + 1):
        click.echo(f"   Step {step}/{time_steps}...")
        df = compute_descriptors(fragments, experiment_id, step)
        insert_descriptors_batch(df)

        if step < time_steps:
            new_fragments = []
            for frag in fragments:
                new_fragments.extend(apply_degradation(frag, mechanism, conditions))
            fragments = new_fragments

    click.echo(f"\n✓ Run complete: {output_label}")
    click.echo(f"  Results written to Supabase — experiment ID {experiment_id}")


if __name__ == "__main__":
    run()