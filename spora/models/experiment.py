"""
spora/models/experiment.py
--------------------------
Data model for a degradation experiment run.
ExperimentSpec is built from CLI arguments and passed into the pipeline.
"""

from pydantic import BaseModel
from typing import Optional


class ExperimentSpec(BaseModel):
    """
    Represents the parameters for a single degradation experiment.
    Created from CLI arguments in scripts/run_degradation.py and
    written to the experiments table in Supabase on run start.

    Example:
        spec = ExperimentSpec(
            label="pla_hydro_60c_2pct",
            polymer_name="PLA",
            mechanism_code="hydrolysis",
            temperature_c=60.0,
            time_steps=10,
            masterbatch_pct=0.02,
            chain_length_n=50,
            run_by="mariana",
        )
    """

    label: str
    polymer_name: str
    mechanism_code: str
    temperature_c: float
    time_steps: int
    masterbatch_pct: Optional[float] = None
    chain_length_n: Optional[int] = 50
    run_by: str = "mariana"
    notes: Optional[str] = None
