# scaled_pilots_onboarding_questionnaire

[Current survey (main)](https://eeca-nz.github.io/scaled_pilots_onboarding_questionnaire/)

[Current survey (dev)](https://eeca-nz.github.io/scaled_pilots_onboarding_questionnaire/dev/)

Collaboratively editable survey instrument ported from **HEEP2 Light Survey (Dec 2023)** for scaled DF pilots.

## Repository structure

- `questionnaire/sections/` - canonical YAML question files
- `questionnaire/schema/` - questionnaire schema
- `questionnaire/codebook.csv` - generated codebook
- `questionnaire/review.html` - generated human-friendly review form
- `scripts/validate_questionnaire.py` - validates YAML content
- `scripts/build_questionnaire_outputs.py` - builds `codebook.csv` + `review.html`
- `docs/` - governance, decision log, usage
- `.github/workflows/` - validation and GitHub Pages deploy workflows

## Review page

Generated review page: `questionnaire/review.html`

Features:
- interactive radio/checkbox inputs
- fillable numeric fields
- free-text response areas
- optional analysis code display toggle

## GitHub Actions

- `validate-questionnaire.yml`: runs validation/build checks on pull requests
- `deploy-pages.yml`: on push to any branch, deploys a combined Pages site with `/` built from `main` and `/dev/` built from `dev` or the pushed non-`main` branch

## Source

Source PDF used for porting: `heep2_light_survey_dec_2023.pdf`
