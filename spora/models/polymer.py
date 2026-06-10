"""
spora/models/polymer.py
-----------------------
Data model for a polymer family.
PolymerSpec is used throughout the pipeline to pass polymer
information between modules in a structured, validated way.
"""

from pydantic import BaseModel
from typing import Optional


class PolymerSpec(BaseModel):
    """
    Represents a polymer family in the SPORA pipeline.
    Matches the structure of the polymers table in Supabase.

    Example:
        pla = PolymerSpec(
            name="PLA",
            smiles_monomer="CC(OC(=O))n",
            polymer_class="polyester",
            glass_transition_c=60,
            melt_temp_c=175,
        )
    """

    id: Optional[int] = None
    name: str
    smiles_monomer: str
    smiles_polymer: Optional[str] = None
    polymer_class: str
    glass_transition_c: Optional[float] = None
    melt_temp_c: Optional[float] = None
    notes: Optional[str] = None
