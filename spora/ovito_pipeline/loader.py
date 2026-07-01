"""
spora/ovito_pipeline/loader.py
--------------------------------
Loads XYZ conformer files produced by the RDKit pipeline.
"""

from pathlib import Path

ELEMENT_COLORS = {
    "C": "#1B2340",
    "O": "#6DCFB2",
    "N": "#4A5568",
    "H": "#CCCCCC",
}

ELEMENT_SIZES = {
    "C": 80,
    "O": 100,
    "N": 90,
    "H": 30,
}


def parse_xyz(filepath: str) -> dict:
    atoms = []
    with open(filepath) as f:
        lines = f.readlines()
    n_atoms = int(lines[0].strip())
    comment = lines[1].strip()
    for line in lines[2:2 + n_atoms]:
        parts = line.strip().split()
        if len(parts) >= 4:
            atoms.append({
                "symbol": parts[0],
                "x": float(parts[1]),
                "y": float(parts[2]),
                "z": float(parts[3]),
                "color": ELEMENT_COLORS.get(parts[0], "#888888"),
                "size": ELEMENT_SIZES.get(parts[0], 50),
            })
    return {"n_atoms": n_atoms, "comment": comment, "atoms": atoms}


def load_conformer_series(conformer_dir: str) -> list:
    path = Path(conformer_dir)
    xyz_files = sorted(path.glob("step_*.xyz"))
    return [parse_xyz(str(f)) for f in xyz_files]
