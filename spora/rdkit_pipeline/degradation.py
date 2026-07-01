"""
spora/rdkit_pipeline/degradation.py
-------------------------------------
Stage 2 of the pipeline: apply degradation reactions to polymer molecules.

TODO (Mariana — Week 3): Implement apply_degradation() using RDKit's
AllChem.ReactionFromSmarts() and RunReactants() to actually break bonds
based on the reaction_smarts stored in the degradation_mechanisms table.
"""

from rdkit import Chem


def apply_degradation(mol, mechanism: str, conditions: dict) -> list:
    """
    Apply one degradation step to a molecule and return the resulting fragments.

    Args:
        mol: RDKit molecule object representing the current polymer chain
        mechanism: degradation mechanism code (e.g. 'hydrolysis', 'thermo_oxidation_ldpe')
        conditions: dict with keys like 'temperature_c' and 'masterbatch_pct'

    Returns:
        List of RDKit molecule objects — the fragments after degradation.
        If no reaction occurs, returns the original molecule in a list.

    TODO: implement actual bond scission using reaction_smarts from the database.
    For now returns the molecule unchanged as a placeholder.
    """
    if mol is None:
        return []

    # Placeholder — returns molecule unchanged until bond scission is implemented
    return [mol]
