"""
spora/rdkit_pipeline/smiles_builder.py
---------------------------------------
Stage 1 of the pipeline: build polymer SMILES strings from a monomer.

TODO: Implement build_polymer_smiles() to generate an oligomer
      with n_repeat repeat units from the monomer SMILES.
"""

from rdkit import Chem


def build_polymer_smiles(monomer_smiles: str, n_repeat: int) -> str:
    """
    Build a representative polymer SMILES string by repeating a monomer unit.

    Args:
        monomer_smiles: SMILES string of the repeat unit (e.g. 'CC(OC(=O))n' for PLA)
        n_repeat: number of repeat units in the oligomer

    Returns:
        SMILES string of the resulting oligomer

    Raises:
        ValueError: if the monomer SMILES is invalid
    """
    mol = Chem.MolFromSmiles(monomer_smiles)
    if mol is None:
        raise ValueError(f"Invalid monomer SMILES: {monomer_smiles}")

    # TODO: implement proper repeat-unit polymerisation logic
    # For now, return the monomer as a placeholder
    return monomer_smiles
