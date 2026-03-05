# scaled_pilots_onboarding_questionnaire

[Current survey (main)](https://eeca-nz.github.io/scaled_pilots_onboarding_questionnaire/)

[Current survey (dev)](https://eeca-nz.github.io/scaled_pilots_onboarding_questionnaire/dev/)

Collaboratively editable questionnaire for **Scaled Demand Flexibility Pilots**.

Organizes and synthesizes questionnaire questions taken from recent projects with overlapping concerns:
* HEEP2 (Light)
* Heat Pump Water Heater pilot questionnaire and system data
* Warmer Kiwi Homes evaluation research

The goal of this repository is to provide a disposable platform that can help us develop a visible prototype onboarding questionnaire for the Demand Flexibility Scaled Pilots.

It is expected that the number of questions will change as the necessary conversations take place.

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
- `deploy-pages.yml`: on push to any branch, publishes both:
  - `/` from `main`
  - `/dev/` from the pushed non-main branch (or `dev` when pushing `main`)

## References

- HEEP2-Light-Survey_Dec 2023.pdf
- https://www.branz.co.nz/healthy-homes-research/heep2-energy-use-living-conditions-in-nz-homes/information-for-researchers/
- https://d39d3mj7qio96p.cloudfront.net/media/documents/HEEP2-Full-HouseholderSurvey_-_paper_copy.pdf