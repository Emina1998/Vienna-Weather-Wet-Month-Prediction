# WP3 Documentation Audit Report

Audit date: 2026-05-24  
Repository: FAIR Vienna Wet Month Prediction  
Assignment source checked: `2026-Dast-Excercise-Part3.pdf`

## Executive Summary

The repository contains several useful WP3 artefacts, especially CodeMeta, Croissant, FAIR4ML metadata, model artefacts, output artefacts, model-card documentation, README documentation, and explicit licence statements. The strongest current WP3 component is T3.4 Croissant: the Croissant file exists, parses as JSON, matches the actual raw CSV columns exactly, and its distribution size/hash match the repository file.

The submission is not WP3-complete yet. The major missing or blocked items are the root `ro-crate-metadata.json`, RO-Crate validation output, `CITATION.cff`, Zenodo DOI badge, TUWRD model/generated-data deposit evidence, and the standards overlap analysis. CodeMeta is present but does not yet satisfy the dependency-generation requirement because `requirements.txt` is mostly unpinned and the CodeMeta dependency versions cannot be traced to pinned requirements. FAIR4ML and the model card are present for both models, but they still depend on TUWRD deposit work and need DOI/contact/version consistency cleanup.

Estimated WP3 completion: **45%**. This estimate is strict and treats DOI/deposit/validation gaps as blockers rather than cosmetic issues.

## Status Table

| Task | Status | Evidence | Main blocker or gap |
|---|---|---|---|
| T3.1 RO-Crate | Missing / blocked | No `ro-crate-metadata.json` in repository root | Create RO-Crate, include all entities/relationships, add real TUWRD DOI identifiers after deposits, run `ro-crate-validator`, store output in `docs/validation/` |
| T3.2 CodeMeta | Partially complete | `codemeta.json` exists and JSON parses | `requirements.txt` is not pinned except `dbrepo`; CodeMeta dependency versions are inconsistent with unpinned requirements and local imports; Python version differs from README |
| T3.3 FAIR4ML | Partially complete, deposit-blocked | `docs/fair4ml/fair4ml_logreg.json` and `docs/fair4ml/fair4ml_randomforest.json` exist and JSON parses | No TUWRD model deposit evidence; not referenced by RO-Crate; model deposit DOI missing; library/runtime versions inconsistent |
| T3.4 Croissant | Complete except final standard-policy check | `docs/croissant/weather_raw_hohewarte_croissant.json` exists, parses, matches raw CSV, and is referenced in README | Assignment PDF mentions QUDT from T2.3; project uses OM-2. Confirm this is accepted or align T2.3/Croissant wording |
| T3.5 Model Card | Partially complete | `docs/model-card.md` exists and covers both models with required core sections and metrics table | Single combined card rather than clearly separate per-model cards; contact information missing; training data DOI/deposit wording needs correction |
| T3.6 Licences | Mostly complete, deposit-blocked | README, `LICENSE`, metadata files, and `docs/licensing.md` state separate input/code/output licences | TUWRD deposit records still need matching licence metadata |
| T3.7 README | Partially complete | README covers purpose, setup, reproduction, DBRepo access, inputs/outputs, licences, contributors, and metadata links | No Zenodo DOI badge; no final RO-Crate/CITATION links to real DOI; some version and standard-consistency issues remain |
| T3.8 Zenodo DOI | Blocked / pending, not failed | README explicitly says badge pending | `CITATION.cff` missing; no Zenodo DOI badge; no evidence of GitHub-Zenodo release integration; do not invent DOI |
| T3.9 Model deposit | Blocked / pending | Model files, FAIR4ML files, model card, and licence text exist locally | No TUWRD model deposit DOI/URL/evidence; related identifiers cannot be completed until Zenodo and generated-data deposit exist |
| T3.10 Generated data deposit | Blocked / pending | Prediction CSVs and figures exist locally | No TUWRD generated-data deposit DOI/URL/evidence; related identifiers cannot be completed until Zenodo and model deposit exist |
| T3.11 Standards overlap analysis | Missing | No `docs/standards_overlap_analysis.md` | Create pairwise RO-Crate/CodeMeta/FAIR4ML/Croissant/Model Card comparison table and discussion |

## Detailed Findings

### T3.1 RO-Crate

Required file `ro-crate-metadata.json` is missing from the repository root. Because the RO-Crate is absent, it cannot currently reference README, source code, input dataset, Croissant metadata, CodeMeta, trained models, outputs, licences, authors, or inter-entity relationships.

The `docs/validation/` directory exists but contains only `.gitkeep`; there is no RO-Crate validation output. `rocrate-validator` is not installed in the local environment, so validation could not be run during this audit.

Fixes needed:

- Create `ro-crate-metadata.json` in the repository root.
- Include entities for README, `codemeta.json`, Croissant metadata, FAIR4ML files, model card, raw input data, DBRepo dataset/view, source code, trained model files, prediction outputs, metrics, figures, licences, and authors.
- Use only real DOI identifiers. For unavailable TUWRD/Zenodo DOIs, use explicit pending notes rather than fake DOI values.
- Run `rocrate-validator` after installation and store output under `docs/validation/`.
- Reference the RO-Crate from README once the file exists.

### T3.2 CodeMeta

`codemeta.json` exists in the repository root and parses successfully as JSON. It uses the CodeMeta 2.0 context, includes project name, version, authors with ORCIDs, MIT licence, Python runtime/language, dependencies, and the GitHub URL as `codeRepository`.

Problems:

- `requirements.txt` contains unpinned dependencies: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `joblib`, and `python-dotenv`. Only `dbrepo==1.13.4` is pinned.
- The assignment requires dependencies to be generated programmatically from `requirements.txt` or `environment.yml` and include version pins. This cannot be satisfied from the current unpinned `requirements.txt`.
- CodeMeta dependency versions do not match the current local imports observed during audit: local imports reported pandas 3.0.3, numpy 2.4.6, scikit-learn 1.7.2, matplotlib 3.10.6, joblib 1.5.2, while CodeMeta lists pandas 3.0.2, numpy 2.4.4, scikit-learn 1.8.0, matplotlib 3.10.8, joblib 1.5.3.
- README says Python 3.11.0, CodeMeta says CPython/Python 3.10, and the audit shell is Python 3.13.9. The repository should choose one supported runtime and state it consistently.

Fixes needed:

- Pin all requirements in `requirements.txt` or add a pinned `environment.yml`.
- Regenerate `codemeta.json` from the pinned dependency source.
- Align Python/runtime version across README, CodeMeta, FAIR4ML, and model-card text.

### T3.3 FAIR4ML

FAIR4ML metadata exists for both expected trained models:

- `docs/fair4ml/fair4ml_logreg.json`
- `docs/fair4ml/fair4ml_randomforest.json`

Both files parse as JSON. Both include algorithm name, library, implementation class, hyperparameters, feature list, target definition, split strategy, evaluation metrics, intended use, out-of-scope uses, limitations, ethical considerations, model artefact paths, and model-card reference.

Metric checks passed against `outputs/predictions/model_metrics_v1.csv` within rounding:

- Logistic Regression: accuracy 0.7467, precision 0.6875, recall 0.44, F1 0.5366.
- Random Forest: accuracy 0.7600, precision 0.7059, recall 0.48, F1 0.5714.

Problems:

- FAIR4ML files are not referenced by RO-Crate because RO-Crate is missing.
- There is no evidence that FAIR4ML files were uploaded alongside the model artefacts in a TUWRD model deposit.
- No model-deposit DOI field is present. The files use GitHub URLs as `@id` for model artefacts and a training dataset identifier `10.70124/wn56q-hvb63`, but the TUWRD model DOI remains unresolved.
- The FAIR4ML library version is `scikit-learn 1.5.1`, while CodeMeta lists `1.8.0`, local import reports `1.7.2`, and `requirements.txt` is unpinned.
- FAIR4ML author lists only Emina Skrijelj. If the model/deposit creators should be all group members, this should be aligned with README/CodeMeta/TUWRD.

Fixes needed:

- Add real TUWRD model deposit DOI and URL after T3.9.
- Reference both FAIR4ML files from the RO-Crate.
- Align package/runtime versions with pinned requirements and CodeMeta.
- Confirm whether model metadata creators should be the single model owner or all deposit creators.

### T3.4 Croissant

`docs/croissant/weather_raw_hohewarte_croissant.json` exists and passes JSON syntax validation. The file describes the repository raw CSV `data/raw/weather_raw_vienna_hohewarte_v1.csv`.

Checks passed:

- Actual raw CSV has 29 columns.
- Croissant declares 29 fields.
- Croissant field order exactly matches the raw CSV header.
- All fields include `dataType`.
- Relevant numeric/measurement fields include `cr:unit`; `NUTS` is correctly text and unitless.
- Distribution `contentUrl` points to an existing file.
- Declared byte size `211328 bytes` matches the file.
- Declared SHA-256 hash matches the file.
- Licence is CC BY 4.0.
- README references the Croissant metadata.
- `docs/croissant/README.md` exists.
- `docs/croissant/validation_notes.md` was added during this audit.

Potential issue:

- The assignment PDF wording says Croissant units should reference QUDT URIs from T2.3. The repository T2.3 material and README use OM-2 unit URIs instead. This is internally consistent with the current project, but the group should confirm whether OM-2 is accepted for final grading or revise T2.3/Croissant to QUDT.

### T3.5 Model Card

`docs/model-card.md` exists. It covers Logistic Regression and Random Forest, includes intended use, out-of-scope uses, training data, evaluation results, a metrics table with precision/recall/F1, limitations, ethical considerations, licence, references, and model artefact filenames.

Fix applied during audit:

- Corrected FAIR4ML references from non-existing `docs/fair4ml/fair4ml_logreg_v1.json` and `docs/fair4ml/fair4ml_randomforest_v1.json` to existing `docs/fair4ml/fair4ml_logreg.json` and `docs/fair4ml/fair4ml_randomforest.json`.

Problems:

- The user requirement asks for a Model Card for each trained model. The current file is a single combined model card. This may be acceptable if instructors accept one combined file, but it is stricter to provide one clearly separated card per model or two files under `docs/model_card/`.
- Contact information is missing.
- The training-data section contains `PLACEHOLDER_TUWRD_MODEL_DEPOSIT_DOI`, which is a model-deposit placeholder and not a training-data DOI. This should be replaced with the correct training dataset DOI/reference and separate model deposit DOI after T3.9.
- RO-Crate reference remains pending because `ro-crate-metadata.json` is missing.

### T3.6 Licences

Licensing is mostly in place. README clearly separates:

- Input data: CC BY 4.0, Stadt Wien / data.gv.at.
- Software/code: MIT, with root `LICENSE`.
- Output/generated data and trained models: CC BY 4.0.

Metadata consistency:

- CodeMeta licence: `MIT`.
- Croissant licence: CC BY 4.0 URL.
- FAIR4ML model licences: CC BY 4.0 URL.
- Model card model licence: CC BY 4.0.
- `docs/licensing.md` was added during this audit as a separate licence summary.

Remaining blocker:

- TUWRD deposit records for models and generated data must explicitly carry the output-data licence.

### T3.7 README

README is substantial and covers project purpose, requirements, setup, reproduction, DBRepo access, input/output artefacts, model performance, file organisation, ontology/unit mappings, DBRepo views/loading/API access, Croissant metadata, licences, contributors, and Zenodo DOI status.

Fixes applied during audit:

- Added a WP3 metadata-files section linking to existing CodeMeta, Croissant, validation notes, FAIR4ML, licensing, model-card, and validation directory paths.
- Added explicit pending note for `ro-crate-metadata.json` and `CITATION.cff`.
- Fixed malformed contributors table so roles, names, and ORCIDs render as a Markdown table.

Remaining gaps:

- Zenodo DOI badge is still pending.
- `CITATION.cff` is missing.
- RO-Crate file and validation links cannot be final until T3.1 is completed.
- Runtime/dependency versions are inconsistent with CodeMeta and unpinned requirements.

### T3.8 Zenodo DOI

This task is blocked/pending and should not be marked failed solely because the DOI does not exist yet.

Current state:

- `CITATION.cff` is missing.
- README has no DOI badge and explicitly says the badge will be added after Zenodo integration.
- No Zenodo DOI was found in the repository.
- No evidence of GitHub-Zenodo integration or release-minted DOI is present.

Fixes needed:

- Enable GitHub-Zenodo integration.
- Create a GitHub release that mints the Zenodo DOI.
- Add the Zenodo DOI badge to README.
- Add `CITATION.cff` with the real Zenodo DOI.
- Add the Zenodo DOI as a related identifier in all TUWRD deposit records.
- Do not create manual Zenodo uploads and do not invent a DOI.

### T3.9 Model Deposit

Local materials required for a model deposit are largely present:

- `outputs/models/model_logreg_v1.pkl`
- `outputs/models/model_randomforest_v1.pkl`
- `docs/fair4ml/fair4ml_logreg.json`
- `docs/fair4ml/fair4ml_randomforest.json`
- `docs/model-card.md`
- `docs/licensing.md`

Blocked items:

- No TUWRD model deposit DOI or URL is present.
- No evidence that the deposit has resource type Model.
- No evidence that DaSt-2026-final community inclusion was requested.
- Related identifiers cannot be complete until Zenodo DOI and generated-data deposit DOI exist.

### T3.10 Generated Data Deposit

Expected generated data artefacts exist locally:

- `outputs/predictions/model_metrics_v1.csv`
- `outputs/predictions/predictions_test_v1.csv`
- `outputs/figures/fig_confusion_matrix_logreg_v1.png`
- `outputs/figures/fig_confusion_matrix_randomforest_v1.png`
- `outputs/figures/fig_model_comparison_v1.png`

Blocked items:

- No TUWRD generated-data deposit DOI or URL is present.
- No evidence that the deposit has resource type Dataset.
- No evidence that DaSt-2026-final community inclusion was requested.
- Related identifiers cannot be complete until Zenodo DOI and model-deposit DOI exist.

### T3.11 Standards Overlap Analysis

`docs/standards_overlap_analysis.md` is missing. This task is not started in the repository.

Fixes needed:

- Create a pairwise matrix comparing RO-Crate, CodeMeta, FAIR4ML, Croissant, and Model Card.
- For each pair, list shared fields, fields unique to each standard, overlaps, conflicts, and inconsistencies.
- Discuss project-specific conflicts already found in this audit, especially creators/authors, version fields, package/runtime versions, licences, DOI fields, model artefact identifiers, and dataset identifiers.

## Cross-File Consistency Findings

| Topic | Current state | Assessment |
|---|---|---|
| Project title | README/CodeMeta use `Vienna Weather Wet-Month Prediction`; audit context uses `FAIR Vienna Wet Month Prediction`; Croissant description includes `FAIR Vienna Wet Month Prediction` | Standardise final title spelling and hyphenation |
| Authors | README and CodeMeta list four ORCID-bearing contributors; FAIR4ML lists only Emina Skrijelj | Confirm creator policy and align where appropriate |
| Licences | Input CC BY 4.0, code MIT, outputs/models CC BY 4.0 | Mostly consistent; deposits pending |
| Version | CodeMeta `2.0.0`; model metadata/card `1.0.0`; artefacts `v1`; README does not define repository release version | Add a clear release/version policy |
| GitHub URL | Consistent: `https://github.com/Emina1998/Vienna-Weather-Wet-Month-Prediction` | OK |
| Zenodo DOI | Missing | Blocked pending T3.8 |
| Dataset source URL | Consistent data.gv.at URL | OK |
| DBRepo names | README uses `weather_measurement_v2` and `weather_measurement_v2_features`; source loader uses the same names | OK |
| Model artefacts | Expected files exist and metadata points to them | OK |
| Output artefacts | Expected prediction and figure files exist | OK |
| Python version | README says 3.11.0; CodeMeta and FAIR4ML say 3.10; audit shell is 3.13.9 | Inconsistent |
| scikit-learn version | FAIR4ML says 1.5.1; CodeMeta says 1.8.0; local import reports 1.7.2; requirements unpinned | Inconsistent |

## Placeholder and DOI Findings

Search terms checked: `TODO`, `PLACEHOLDER`, `TBD`, `to be added`, `will be added`, `update after`, `pending DOI`, `doi`.

Findings:

- README has a pending Zenodo DOI badge note. This is acceptable while T3.8 is blocked.
- `docs/model-card.md` has `PLACEHOLDER_TUWRD_MODEL_DEPOSIT_DOI`. This is acceptable only as a temporary blocked item, but it is currently placed under training data and should be corrected.
- `docs/model-card.md` says RO-Crate is to be added. This is acceptable while T3.1 is incomplete.
- No fake Zenodo DOI was found.
- The FAIR4ML training dataset identifier `10.70124/wn56q-hvb63` looks DOI-like but was not verified externally during this local audit.

## Sensitive Information Scan

Findings:

- `.env` exists locally but is not tracked by Git according to `git ls-files`. `.gitignore` includes `.env`, `.env.local`, and `.env.*.local`.
- No tracked `.env` file was found.
- README and `.env.example` contain placeholder DBRepo username/password fields, not real credentials.
- Source code and notebooks use environment variables, `input()`, or `getpass()` for DBRepo credentials.
- `notebooks/t2_6_api_reimplementation.ipynb` includes output text indicating username/password were configured as `True`, but it does not expose actual values.
- DBRepo database/table IDs are visible in README and `.env.example`. Treat these as non-secret identifiers unless the DBRepo project policy says otherwise.

Recommended cleanup:

- Keep `.env` untracked.
- Before final submission, clear notebook outputs that reveal local configuration state.
- Do not paste real DBRepo credentials into notebooks, README, metadata, or deposits.

## Validation Commands and Results

| Command | Result |
|---|---|
| `pdftotext -layout 2026-Dast-Excercise-Part3.pdf /private/tmp/wp3_assignment.txt` | Passed; PDF text extracted and WP3 requirements confirmed |
| `python -m json.tool codemeta.json` | Passed |
| `python -m json.tool docs/croissant/weather_raw_hohewarte_croissant.json` | Passed |
| `python -m json.tool docs/fair4ml/fair4ml_logreg.json` | Passed |
| `python -m json.tool docs/fair4ml/fair4ml_randomforest.json` | Passed |
| `croissant docs/croissant` | Passed with exit status 0 and no terminal output |
| Croissant raw-column/hash script | Passed; 29 fields match raw CSV exactly and SHA-256 matches |
| FAIR4ML metric comparison script | Passed within rounding against `outputs/predictions/model_metrics_v1.csv` |
| `command -v rocrate-validator` | Not available; RO-Crate validation not run |
| `python -c "import yaml; print('PyYAML available')"` | PyYAML available, but `CITATION.cff` is missing so no YAML file was checked |

## Files Inspected

- `2026-Dast-Excercise-Part3.pdf`
- `README.md`
- `LICENSE`
- `.gitignore`
- `.env.example`
- local untracked `.env` presence, without reporting secret values
- `requirements.txt`
- `codemeta.json`
- `docs/croissant/weather_raw_hohewarte_croissant.json`
- `docs/croissant/README.md`
- `docs/unit_mapping.csv`
- `docs/semantic_mapping.csv`
- `docs/fair4ml/fair4ml_logreg.json`
- `docs/fair4ml/fair4ml_randomforest.json`
- `docs/model-card.md`
- `docs/validation/`
- `data/raw/weather_raw_vienna_hohewarte_v1.csv`
- `outputs/models/model_logreg_v1.pkl`
- `outputs/models/model_randomforest_v1.pkl`
- `outputs/predictions/model_metrics_v1.csv`
- `outputs/predictions/predictions_test_v1.csv`
- `outputs/figures/fig_confusion_matrix_logreg_v1.png`
- `outputs/figures/fig_confusion_matrix_randomforest_v1.png`
- `outputs/figures/fig_model_comparison_v1.png`
- `src/data/load_from_dbrepo.py`
- `src/pipeline/run_experiment.py`
- `src/models/train_model.py`
- `src/models/evaluate_model.py`
- notebooks under `notebooks/`
- SQL files under `sql/`

## Files Modified During Audit

- `README.md`: added metadata-file links, pending RO-Crate/CITATION note, and fixed contributor table.
- `docs/model-card.md`: corrected FAIR4ML filename references.
- `docs/croissant/validation_notes.md`: added Croissant validation notes.
- `docs/licensing.md`: added separate licensing summary.
- `docs/wp3_audit_report.md`: added this audit report.

## Final Checklist Before WP3 Submission

- [ ] Create `ro-crate-metadata.json` in repository root.
- [ ] Validate RO-Crate with `ro-crate-validator`.
- [ ] Save RO-Crate validation output under `docs/validation/`.
- [ ] Pin all dependencies in `requirements.txt` or `environment.yml`.
- [ ] Regenerate `codemeta.json` from pinned dependencies.
- [ ] Align Python and scikit-learn versions across README, CodeMeta, FAIR4ML, model card, and requirements.
- [ ] Confirm whether Croissant/Unit Mapping may use OM-2 or must be changed to QUDT.
- [ ] Add or split model cards so each trained model is clearly covered; add contact information.
- [ ] Replace model-card DOI placeholder with real DOI information once deposits exist.
- [ ] Complete GitHub-Zenodo integration and create a release-minted Zenodo DOI.
- [ ] Add Zenodo DOI badge to README.
- [ ] Add `CITATION.cff` with the real Zenodo DOI.
- [ ] Create TUWRD model deposit with model files, FAIR4ML metadata, model card, licence, and related identifiers.
- [ ] Create TUWRD generated-data deposit with predictions, metrics, figures, licence, and related identifiers.
- [ ] Add real TUWRD DOI/URL identifiers to FAIR4ML and RO-Crate.
- [ ] Create `docs/standards_overlap_analysis.md`.
- [ ] Clear notebook outputs that reveal local configuration state before final release.
- [ ] Verify no `.env` file is tracked.

## Exact Next Actions by Group Member

### Owner A

- T3.1: Build `ro-crate-metadata.json` with all input, code, model, output, licence, author, CodeMeta, Croissant, FAIR4ML, and Model Card entities.
- T3.1: After T3.9/T3.10/T3.8 identifiers exist, insert only real Zenodo/TUWRD identifiers.
- T3.1: Install/run `ro-crate-validator` and place validation output in `docs/validation/`.
- T3.5: Add contact information and make the model card clearly per-model, either with two separate cards or clearly separated per-model sections.
- T3.9: Create the TUWRD model deposit with both `.pkl` model files, FAIR4ML metadata, model card, licence, and related identifiers.

### Owner B

- T3.2: Pin all dependencies in `requirements.txt` or create a pinned `environment.yml`.
- T3.2: Regenerate `codemeta.json` programmatically from the pinned dependency source.
- T3.2: Align runtime and dependency versions across CodeMeta, README, FAIR4ML, and the model card.
- T3.6: Ensure the model and generated-data TUWRD deposits use the output-data licence CC BY 4.0.
- T3.10: Create the TUWRD generated-data deposit for predictions, metrics, figures, confusion matrices, and evaluation outputs.

### Owner C

- T3.3: Update both FAIR4ML files after T3.9 with real TUWRD model deposit DOI/URL.
- T3.3: Resolve creator/version consistency in FAIR4ML.
- T3.7: Update README after T3.8 with the Zenodo DOI badge and final metadata/DOI links.
- T3.11: Create `docs/standards_overlap_analysis.md` with all pairwise standard comparisons and project-specific inconsistencies.

### Owner D

- T3.4: Confirm with the assignment/team whether OM-2 unit URIs are acceptable or whether Croissant/T2.3 must be changed to QUDT.
- T3.4: Keep `docs/croissant/validation_notes.md` current after any Croissant edits.
- T3.8: Enable GitHub-Zenodo integration, create the release that mints the Zenodo DOI, add README badge, and add `CITATION.cff`.
- T3.8: Add the Zenodo DOI as a related identifier in all TUWRD deposit records.
