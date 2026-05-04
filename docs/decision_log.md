# Decision Log

## 2026-03-04 - Split hot water from heating/cooling section
- Replaced the combined `Hot water, heating and cooling` section with two sections:
  - `Hot water` (all `HW_*` questions)
  - `Heating and cooling` (`HEAT_*`, `OA_30`-`HEAT_33`, `DF_*`, `HOME_COND_*`)
- Preserved question IDs and within-section order; only section grouping changed.
- Updated generated outputs (`codebook.csv`, `review.html`) via standard build script.

## 2026-03-04 - Matrix-style review rendering for single-select-by-row questions
- Added matrix-style rendering in `review.html` for questions that are conceptually "one choice per row".
- `HW_29` now renders as a row/column matrix (Showers, Baths, Washing dishes, Laundry x frequency bands) with radio buttons, while staying the same YAML question.
- Combined room-heating frequency display in review by rendering `HEAT_17` and `HEAT_30B` as one matrix block with one selection per row.
- Added multi-select matrix rendering for heating appliance coverage by room, combining `HEAT_18`, `HEAT_31B`, and `HEAT_31C` into a single 3-row matrix block in review output.
- No schema/widget type changes were introduced; this is a presentation-layer change in `scripts/build_questionnaire_outputs.py`.

## 2026-03-04 - Removed explicit gas end-use follow-up
- Removed `GAS_01` and `GAS_02` from `About your house or flat`.
- Reverted `HOME_10` skip logic to no gas follow-up.
- Rationale: gas end-use can be inferred from existing hot water, cooktop, and heating questions, reducing respondent burden.

## 2026-03-04 - HPWH hot water extension and gas end-use follow-up
- Added a new `Hot water details` and `Hot water usage behaviour` block in `Hot water, heating and cooling`, placed immediately after `HW_16` and before `HEAT_17`.
- Added HPWH/system detail questions `HW_23` to `HW_29` (brand/model, HP type split/integral, indoor/outdoor location, tank volume, age known + age band).
- Added hot water behaviour questions `HW_29` to `HW_35`, including:
  - Encoded frequency capture as a single `multi_choice` question (`HW_29`) using flat activity-frequency option codes (no grid/matrix type introduced).
  - Follow-up usage/attitude items (other uses, shower duration, dishwashing method, expected change and reason, monitoring effort).
- Added gas end-use breakdown directly after `HOME_10` in `About your house or flat` for clearer dependency on energy-source selection:
  - `GAS_01` captures gas end uses (water heating/cooking/heating/other/unsure), conditionally asked when `HOME_10` includes `NATURAL_GAS` or `LPG`.
  - `GAS_02` captures free-text `OTHER` gas use detail.
- Updated renderer (`scripts/build_questionnaire_outputs.py`) so `HW_29` remains one YAML question but is displayed in grouped activity headings (Showers, Baths, Washing dishes, Laundry) in `review.html`.
- Added a non-blocking validator warning/TODO for runtime enforcement of one frequency per activity in `HW_29`.

## 2026-03-04 - Demand Flexibility extension questions
- Added new demand flexibility questions to `Hot water, heating and cooling` after existing cooling question `OA_30` to keep all behaviour/comfort-flexibility items in one section without altering existing question order.
- Added:
  - `DF_01` weekday home-presence profile (`multi_choice`) with notes on exclusive combinations (`ALL_OR_MOST_OF_THE_TIME` and `HIGHLY_VARIABLE` versus time bands).
  - `DF_02` pricing-driven timing behaviour (`single_choice`) with conditional free-text follow-up `DF_03`.
  - `DF_04` heating constrained by cost (`single_choice` frequency scale).
  - `DF_05` indoor winter clothes-drying frequency (`single_choice`).
  - `HOME_COND_01` to `HOME_COND_03` lightweight winter home-condition indicators (`single_choice` common scale).
- Implemented optional refinement near existing dehumidifier capture:
  - Added `OA_31` (dehumidifier use reasons, conditional on `OA_30` including `DEHUMIDIFIER`).
  - Added `HEAT_33` free-text follow-up when `OA_31` includes `OTHER`.
- No new response/widget types added; retained existing YAML schema types and review renderer patterns.

## 2026-03-03 - Scaled Demand Flexibility Pilots restructuring
- Rebranded questionnaire and generated review output to Scaled Demand Flexibility Pilots.
- Added new top-level `Administrative details` section (`ADMIN_01` to `ADMIN_14`).
- Moved `HH_19`, `HH_20`, and `HH_21` into `About your house or flat` and retained existing IDs.
- Added household composition change questions (`HH_COMP_22` to `HH_COMP_25`).
- Added new sections and questions: `Other appliances` (`OA_26` to `HEAT_33`), `Connection details` (`CONN_33` placeholder), and `Solar and battery` (`SOLAR_34` to `SOLAR_40`, `BATT_38` to `BATT_39`).
- Regenerated `questionnaire/codebook.csv` and `questionnaire/review.html` from YAML after structural changes.
- Added vehicle profiling block in `Solar PV, battery and Vehicle charging`: `VEH_01` to `VEH_08` covering vehicle count/type/size/km band, charging context, charging location/home setup, and replacement intent.

## 2026-03-02 - v0.1 baseline questionnaire setup
- Established the initial YAML-based canonical questionnaire structure.
- Preserved legacy question order and wording for baseline continuity.
- Added placeholder `purpose` values and TODO notes where ambiguity exists.
- Added validation/build scripts and CI scaffold for collaboration workflows.
