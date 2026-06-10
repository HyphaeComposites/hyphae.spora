-- =============================================================================
-- SPORA — Hyphae Composites Computational Polymer Research Pipeline
-- Database Schema v1.0
-- PostgreSQL 15+ / Supabase
--
-- Apply via Supabase SQL Editor or:
--   psql "$DATABASE_URL" -f spora/db/schema.sql
--
-- ⚠️  WARNING: This script drops and recreates all tables.
--     Coordinate with Mariana before running against the shared Supabase project.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- CLEAN SLATE (safe drop in dependency order)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS visualizations       CASCADE;
DROP TABLE IF EXISTS descriptors          CASCADE;
DROP TABLE IF EXISTS experiments          CASCADE;
DROP TABLE IF EXISTS degradation_mechanisms CASCADE;
DROP TABLE IF EXISTS polymers             CASCADE;


-- -----------------------------------------------------------------------------
-- 1. POLYMERS
--    Master registry of all polymer families supported by the pipeline.
--    Populated once via scripts/ingest_polymer.py — do not insert manually.
-- -----------------------------------------------------------------------------
CREATE TABLE polymers (
    id                  SERIAL          PRIMARY KEY,
    name                TEXT            NOT NULL UNIQUE,          -- e.g. 'PLA', 'PETG'
    smiles_monomer      TEXT            NOT NULL,                 -- monomer SMILES
    smiles_polymer      TEXT,                                     -- representative oligomer (n=10)
    polymer_class       TEXT            NOT NULL,                 -- 'polyester' | 'ABS' | 'polyolefin' | ...
    glass_transition_c  FLOAT,                                    -- Tg °C (literature)
    melt_temp_c         FLOAT,                                    -- Tm °C (literature)
    notes               TEXT,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  polymers                  IS 'Master registry of polymer families supported by the SPORA pipeline.';
COMMENT ON COLUMN polymers.smiles_monomer   IS 'Canonical SMILES of the repeat unit / monomer.';
COMMENT ON COLUMN polymers.smiles_polymer   IS 'Representative oligomer SMILES with n=10 repeat units.';
COMMENT ON COLUMN polymers.polymer_class    IS 'Broad material class: polyester, polyolefin, ABS, etc.';

-- Seed data — the five polymers in scope for v1
INSERT INTO polymers (name, smiles_monomer, polymer_class, glass_transition_c, melt_temp_c, notes) VALUES
    ('PLA',  'CC(OC(=O))n',                           'polyester',   60,  175, 'Polylactic acid — primary target polymer for Hyphae kiosk'),
    ('PETG', 'OCCOC(=O)c1ccc(cc1)C(=O)O',            'polyester',   80,  230, 'Polyethylene terephthalate glycol — common in 3D printing'),
    ('ABS',  'C=Cc1ccccc1.C=CC#N.C=CC=C',            'ABS',         105, NULL,'Acrylonitrile butadiene styrene — blend, no single Tm'),
    ('PP',   'CC(C)C',                                'polyolefin',  -20, 165, 'Polypropylene isotactic approximation'),
    ('HDPE', 'CC',                                    'polyolefin', -125, 130, 'High-density polyethylene simplified repeat unit');


-- -----------------------------------------------------------------------------
-- 2. DEGRADATION_MECHANISMS
--    Lookup table for reaction types. Keeps mechanism names normalised across runs.
-- -----------------------------------------------------------------------------
CREATE TABLE degradation_mechanisms (
    id                   SERIAL   PRIMARY KEY,
    code                 TEXT     NOT NULL UNIQUE,   -- CLI flag value e.g. 'hydrolysis'
    name                 TEXT     NOT NULL,           -- full name
    applicable_polymers  TEXT[],                      -- array of polymer names
    reaction_smarts      TEXT,                        -- SMARTS pattern for RDKit bond cleavage
    notes                TEXT
);

COMMENT ON TABLE  degradation_mechanisms                    IS 'Lookup table for degradation reaction types used by the RDKit pipeline.';
COMMENT ON COLUMN degradation_mechanisms.reaction_smarts    IS 'SMARTS pattern passed to RDKit AllChem.ReplaceSubstructs for bond cleavage simulation.';

INSERT INTO degradation_mechanisms (code, name, applicable_polymers, notes) VALUES
    ('hydrolysis',       'Hydrolytic chain scission',        ARRAY['PLA','PETG'],        'Ester bond cleavage in presence of water'),
    ('thermal',          'Thermal depolymerisation',         ARRAY['PLA','ABS','PP'],    'High-temperature backbone breakdown'),
    ('thermo_oxidative', 'Thermo-oxidative degradation',     ARRAY['PP','HDPE','ABS'],   'Oxygen-assisted thermal chain scission'),
    ('uv_scission',      'UV-induced chain scission',        ARRAY['ABS','PP'],          'Norrish type I/II photodegradation'),
    ('glycolysis',       'Glycolysis',                       ARRAY['PETG'],              'Diol-assisted ester bond transesterification');


-- -----------------------------------------------------------------------------
-- 3. EXPERIMENTS
--    One row per pipeline run. Central table — all results reference this.
--    Written automatically by scripts/run_degradation.py — do not insert manually.
-- -----------------------------------------------------------------------------
CREATE TABLE experiments (
    id                      SERIAL          PRIMARY KEY,
    label                   TEXT            NOT NULL UNIQUE,  -- from --output-label CLI flag
    polymer_id              INT             NOT NULL REFERENCES polymers(id),
    mechanism_id            INT             NOT NULL REFERENCES degradation_mechanisms(id),
    temperature_c           FLOAT           NOT NULL,
    time_steps              INT             NOT NULL,
    masterbatch_pct         FLOAT,                            -- weight fraction 0–1 (NULL = no additive)
    chain_length_n          INT,                              -- repeat units in starting polymer
    rdkit_version           TEXT            NOT NULL,         -- pinned for reproducibility
    git_sha                 TEXT            NOT NULL,         -- commit SHA of code that produced this run
    run_by                  TEXT            NOT NULL,         -- initials / username
    started_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    finished_at             TIMESTAMPTZ,                      -- NULL while running
    status                  TEXT            NOT NULL DEFAULT 'running'
                                            CHECK (status IN ('running','completed','failed')),
    notes                   TEXT
);

COMMENT ON TABLE  experiments               IS 'One row per SPORA pipeline run. Immutable once status = completed.';
COMMENT ON COLUMN experiments.label         IS 'Human-readable run identifier set via --output-label CLI flag. Format: {polymer}_{mechanism}_{temp}c_{masterbatch}.';
COMMENT ON COLUMN experiments.masterbatch_pct IS 'Hyphae masterbatch additive concentration as weight fraction (0.02 = 2%). NULL means no additive was applied.';
COMMENT ON COLUMN experiments.git_sha       IS 'Full Git commit SHA — ensures exact code version is always traceable.';

CREATE INDEX idx_experiments_polymer    ON experiments(polymer_id);
CREATE INDEX idx_experiments_status     ON experiments(status);
CREATE INDEX idx_experiments_started_at ON experiments(started_at DESC);


-- -----------------------------------------------------------------------------
-- 4. DESCRIPTORS
--    Computed RDKit molecular descriptors for every fragment at every time step.
--    High-volume table — uses BIGSERIAL. Always insert via bulk COPY (see queries.py).
-- -----------------------------------------------------------------------------
CREATE TABLE descriptors (
    id                  BIGSERIAL   PRIMARY KEY,
    experiment_id       INT         NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    time_step           INT         NOT NULL,         -- 0 = pristine / untreated
    molecule_idx        INT         NOT NULL,         -- index within the fragment pool at this step
    smiles              TEXT        NOT NULL,         -- SMILES of this fragment
    mol_weight          FLOAT,                        -- molecular weight (Da)
    num_rings           INT,
    num_hbd             INT,                          -- H-bond donors
    num_hba             INT,                          -- H-bond acceptors
    logp                FLOAT,                        -- Wildman-Crippen logP
    tpsa                FLOAT,                        -- topological polar surface area (Å²)
    num_rot_bonds       INT,                          -- rotatable bonds
    num_stereo_centers  INT,
    chain_length        INT                           -- estimated remaining repeat units
);

COMMENT ON TABLE  descriptors               IS 'RDKit molecular descriptors per fragment per time step. High-volume — insert via bulk COPY only.';
COMMENT ON COLUMN descriptors.time_step     IS '0 = pristine starting material. Increments by 1 per degradation step.';
COMMENT ON COLUMN descriptors.chain_length  IS 'Estimated remaining polymer chain length in repeat units after fragmentation.';

CREATE INDEX idx_descriptors_experiment ON descriptors(experiment_id);
CREATE INDEX idx_descriptors_timestep   ON descriptors(experiment_id, time_step);


-- -----------------------------------------------------------------------------
-- 5. VISUALIZATIONS
--    Metadata for every OVITO render. Links outputs back to the experiment
--    that produced them so poster figures are always traceable.
-- -----------------------------------------------------------------------------
CREATE TABLE visualizations (
    id              SERIAL          PRIMARY KEY,
    experiment_id   INT             NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    mode            TEXT            NOT NULL CHECK (mode IN ('single','comparison','timelapse')),
    output_path     TEXT            NOT NULL,          -- relative path inside visualizations/
    file_type       TEXT            NOT NULL CHECK (file_type IN ('png','mp4')),
    ovito_version   TEXT            NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  visualizations            IS 'OVITO render metadata. Every image and video is linked to the experiment that produced it.';
COMMENT ON COLUMN visualizations.output_path IS 'Path relative to repo root, e.g. visualizations/pla_hydro_60c_2pct/comparison.png';

CREATE INDEX idx_visualizations_experiment ON visualizations(experiment_id);


-- -----------------------------------------------------------------------------
-- VERIFICATION — run this block to confirm everything was created correctly
-- -----------------------------------------------------------------------------
DO $$
DECLARE
    tbl TEXT;
    expected TEXT[] := ARRAY['polymers','degradation_mechanisms','experiments','descriptors','visualizations'];
BEGIN
    FOREACH tbl IN ARRAY expected LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = tbl
        ) THEN
            RAISE EXCEPTION 'Table % was not created — check for errors above.', tbl;
        END IF;
    END LOOP;
    RAISE NOTICE '✓ All 5 SPORA tables created successfully.';
END $$;
