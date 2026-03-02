# Questionnaire Governance

## Purpose
This repository stores the canonical questionnaire instrument used for scaled DF pilots.

## Change Rules
- Keep edits in YAML under `questionnaire/sections/` so changes are diff-friendly.
- Preserve source wording unless there is an approved decision to change it.
- If a change alters question meaning, create a new `id` and deprecate the old question rather than mutating in place.
- Use `notes` to capture implementation guidance and unresolved interpretation questions.

## PR Review Expectations
- Every PR should list affected question IDs.
- Reviewers should verify:
  - wording fidelity to source,
  - response type and option-code integrity,
  - skip logic behavior,
  - provenance page references,
  - expected downstream analysis impact.
- At least one reviewer should confirm no silent meaning changes were introduced.

## Versioning Guidance
- Record material instrument decisions in `docs/decision_log.md`.
- Use semantic version-like labels in the decision log (`v0.1`, `v0.2`, etc.) for major instrument milestones.
