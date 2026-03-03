# Decision Log

## 2026-03-03 - Scaled Demand Flexibility Pilots restructuring
- Rebranded questionnaire and generated review output to Scaled Demand Flexibility Pilots.
- Added new top-level `Administrative details` section (`ADMIN_01` to `ADMIN_14`).
- Moved `HH_19`, `HH_20`, and `HH_21` into `About your house or flat` and retained existing IDs.
- Added household composition change questions (`HH_COMP_22` to `HH_COMP_25`).
- Added new sections and questions: `Other appliances` (`OA_26` to `OA_32`), `Connection details` (`CONN_33` placeholder), and `Solar and battery` (`SOLAR_34` to `SOLAR_40`, `BATT_38` to `BATT_39`).
- Regenerated `questionnaire/codebook.csv` and `questionnaire/review.html` from YAML after structural changes.
- Added vehicle profiling block in `Solar PV, battery and Vehicle charging`: `VEH_01` to `VEH_08` covering vehicle count/type/size/km band, charging context, charging location/home setup, and replacement intent.

## 2026-03-02 - v0.1 baseline questionnaire setup
- Established the initial YAML-based canonical questionnaire structure.
- Preserved legacy question order and wording for baseline continuity.
- Added placeholder `purpose` values and TODO notes where ambiguity exists.
- Added validation/build scripts and CI scaffold for collaboration workflows.
