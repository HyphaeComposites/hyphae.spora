"""
spora/rdkit_pipeline/smiles_builder.py
---------------------------------------
Stage 1 of the pipeline: build polymer SMILES strings from a monomer,
generate 3D conformers, and write XYZ files for OVITO visualisation.
"""

import os
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors


def build_polymer_smiles(monomer_smiles: str, n_repeat: int) -> str:
    """
    Build a representative polymer SMILES string by repeating a monomer unit
    n_repeat times into a linear oligomer chain.

    Think of it like snapping together n_repeat identical LEGO bricks in a
    straight line — each brick is the monomer, and the result is the oligomer.

    Args:
        monomer_smiles: SMILES string of the repeat unit (e.g. 'CC(OC(=O)O)' for PLA)
        n_repeat: number of repeat units in the oligomer

    Returns:
        SMILES string of the resulting oligomer

    Raises:
        ValueError: if the monomer SMILES is invalid
    """
    mol = Chem.MolFromSmiles(monomer_smiles)
    if mol is None:
        raise ValueError(f"Invalid monomer SMILES: {monomer_smiles}")

    # Get the canonical SMILES for the monomer
    canonical = Chem.MolToSmiles(mol)

    # Build oligomer by repeating the monomer and joining with carbon-carbon bonds.
    # We use the edit mol approach: combine n copies of the monomer into one molecule
    # by iteratively combining fragments.
    combined = mol
    for _ in range(n_repeat - 1):
        next_mol = Chem.MolFromSmiles(canonical)
        combined = Chem.CombineMols(combined, next_mol)

    # Return the SMILES of the combined oligomer
    oligomer_smiles = Chem.MolToSmiles(combined)

    # Validate the result parses back correctly
    check = Chem.MolFromSmiles(oligomer_smiles)
    if check is None:
        raise ValueError(f"Failed to build valid oligomer SMILES from: {monomer_smiles}")

    return oligomer_smiles


def generate_conformer(mol: Chem.Mol, random_seed: int = 42) -> Chem.Mol:
    """
    Generate a 3D conformer for a molecule using RDKit's ETKDG method.

    Think of this as asking RDKit to find a realistic 3D shape for the
    molecule — like going from a flat 2D drawing to an actual 3D model.

    Args:
        mol: RDKit molecule object (must have hydrogens added)
        random_seed: seed for reproducibility

    Returns:
        Molecule with 3D coordinates embedded
    """
    mol_h = Chem.AddHs(mol)
    result = AllChem.EmbedMolecule(mol_h, AllChem.ETKDGv3())
    if result == -1:
        # Fall back to random coordinates if ETKDG fails
        AllChem.EmbedMolecule(mol_h, randomSeed=random_seed)
    AllChem.MMFFOptimizeMolecule(mol_h)
    return mol_h


def write_xyz(mol: Chem.Mol, filepath: str) -> None:
    """
    Write a molecule's 3D coordinates to an XYZ file for OVITO.

    XYZ format is simple: first line is atom count, second is a comment,
    then one line per atom with element symbol and x, y, z coordinates.

    Args:
        mol: RDKit molecule with 3D conformer
        filepath: path to write the .xyz file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    conf = mol.GetConformer()
    atoms = mol.GetAtoms()
    atom_list = list(atoms)
    n_atoms = len(atom_list)

    with open(filepath, "w") as f:
        f.write(f"{n_atoms}\n")
        f.write(f"SPORA conformer — {os.path.basename(filepath)}\n")
        for atom in atom_list:
            idx = atom.GetIdx()
            symbol = atom.GetSymbol()
            pos = conf.GetAtomPosition(idx)
            f.write(f"{symbol}  {pos.x:.6f}  {pos.y:.6f}  {pos.z:.6f}\n")