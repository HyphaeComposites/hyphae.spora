"""
spora/rdkit_pipeline/descriptors.py
--------------------------------------
Stage 3 of the pipeline: compute molecular descriptors for a list of fragments.

These descriptors are what gets stored in the descriptors table in Supabase
and form the core scientific data of every SPORA experiment.
"""

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from typing import List


def compute_descriptors(mol_list: List[Chem.Mol], experiment_id: int, time_step: int) -> pd.DataFrame:
    """
    Compute RDKit molecular descriptors for a list of molecule fragments.

    Args:
        mol_list: list of RDKit Mol objects at a given time step
        experiment_id: the database id of the current experiment
        time_step: which degradation step this is (0 = pristine)

    Returns:
        DataFrame with one row per molecule and columns matching
        the descriptors table schema.
    """
    records = []
    for idx, mol in enumerate(mol_list):
        if mol is None:
            continue
        records.append({
            "experiment_id":     experiment_id,
            "time_step":         time_step,
            "molecule_idx":      idx,
            "smiles":            Chem.MolToSmiles(mol),
            "mol_weight":        Descriptors.MolWt(mol),
            "num_rings":         rdMolDescriptors.CalcNumRings(mol),
            "num_hbd":           rdMolDescriptors.CalcNumHBD(mol),
            "num_hba":           rdMolDescriptors.CalcNumHBA(mol),
            "logp":              Descriptors.MolLogP(mol),
            "tpsa":              Descriptors.TPSA(mol),
            "num_rot_bonds":     rdMolDescriptors.CalcNumRotatableBonds(mol),
            "num_stereo_centers":rdMolDescriptors.CalcNumAtomStereoCenters(mol),
            "chain_length":      None,  # TODO: implement chain length estimation
        })
    return pd.DataFrame(records)
