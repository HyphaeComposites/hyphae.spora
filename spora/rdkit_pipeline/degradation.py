"""
spora/rdkit_pipeline/degradation.py
-------------------------------------
Stage 2 of the pipeline: apply degradation reactions to polymer molecules.

How it works:
    Each call to apply_degradation() represents one degradation step — one
    pass through the extruder, one thermal cycle, one time unit of exposure.
    The function takes a molecule and returns a list of fragments.

    Think of it like snapping a long chain at one weak point — the result
    is two shorter pieces. At higher temperatures, the chain snaps more
    easily. The masterbatch additive acts like a stabilizer, making the
    chain harder to snap.

Mechanism implemented:
    thermo_oxidation_ldpe: Random C-C backbone scission under thermal stress.
    SMARTS: [CH2:1][CH2:2] >> [CH2:1].[CH2:2]
    This breaks one C-C bond per step, selected randomly from all available
    backbone bonds. Probability of scission scales with temperature and is
    reduced by masterbatch concentration.

TODO (Mariana — Week 3): Add hydrolysis mechanism for PLA using ester bond
    cleavage SMARTS. The reaction_smarts column in degradation_mechanisms
    table already has the pattern — load it from the database and apply it
    using AllChem.ReactionFromSmarts() and RunReactants().
"""

import random
from rdkit import Chem
from rdkit.Chem import rdChemReactions


MECHANISM_SMARTS = {
    "thermo_oxidation_ldpe": "[CH2:1][CH2:2]>>[CH2:1].[CH2:2]",
    "thermal":               "[CH2:1][CH2:2]>>[CH2:1].[CH2:2]",
    "hydrolysis":            "[C:1](=[O:2])[O:3][C:4]>>[C:1](=[O:2])[OH].[C:4]",
}


def apply_degradation(mol, mechanism: str, conditions: dict) -> list:
    """
    Apply one degradation step to a molecule and return the resulting fragments.

    Args:
        mol: RDKit molecule object representing the current polymer chain
        mechanism: degradation mechanism code
        conditions: dict with 'temperature_c' and 'masterbatch_pct'

    Returns:
        List of RDKit molecule objects after one degradation step.
    """
    if mol is None:
        return []

    temperature_c = conditions.get("temperature_c", 25)
    masterbatch_pct = conditions.get("masterbatch_pct", None)

    smarts = MECHANISM_SMARTS.get(mechanism)
    if smarts is None:
        return [mol]

    rxn = rdChemReactions.ReactionFromSmarts(smarts)
    if rxn is None:
        return [mol]

    base_prob = (temperature_c - 20) / 200.0
    base_prob = max(0.0, min(base_prob, 0.9))

    if masterbatch_pct and masterbatch_pct > 0:
        base_prob *= max(0.0, 1.0 - masterbatch_pct * 15)

    seed = hash(Chem.MolToSmiles(mol)) % 10000
    rng = random.Random(seed)

    if rng.random() > base_prob:
        return [mol]

    all_products = rxn.RunReactants((mol,))
    if not all_products:
        return [mol]

    chosen = rng.choice(all_products)

    fragments = []
    for p in chosen:
        try:
            Chem.SanitizeMol(p)
            if p.GetNumAtoms() > 0:
                fragments.append(p)
        except Exception:
            pass

    return fragments if fragments else [mol]
