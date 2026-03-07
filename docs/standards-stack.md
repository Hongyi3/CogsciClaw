# Standards stack

## Principle

Wrap existing standards and tools before inventing new formats.

## Recommended stack by lane

| Lane | Standard / tool | Role | Phase |
|---|---|---|---|
| Behavioral data | Psych-DS | organize behavioral datasets | v1 |
| Questionnaires | ReproSchema | represent structured assessments and questionnaires | v1.1 |
| Cognitive ontology | Cognitive Atlas | map tasks, contrasts, concepts, disorders | v1 |
| Browser tasks | jsPsych | build behavioral tasks in the browser | v1 |
| Lab / hybrid tasks | PsychoPy | build controlled experiments for lab and web-adjacent use | v1 |
| Event semantics | HED | machine-actionable event annotation | v1 |
| Neuroimaging structure | BIDS | standardize neuroimaging and associated data | v1 for EEG/MEG |
| EEG/MEG IO | MNE-BIDS | read/write BIDS-compatible EEG/MEG datasets | v1 |
| EEG/MEG analysis | MNE-Python | preprocessing and analysis | v1 |
| fMRI preprocessing | fMRIPrep | robust preprocessing wrapper, not reinvention | later |
| Neurophysiology | NWB | structured neurophysiology data | later |
| Neurophysiology archive | DANDI | archive and validation ecosystem | later |
| Bayesian modeling | PyMC | general Bayesian modeling backbone | v1 |
| Drift diffusion | HDDM | hierarchical DDM workflows | v1 |
| Diagnostics | ArviZ | diagnostics, PPC, summaries | v1 |
| Provenance | RO-Crate / PROV | machine-readable provenance packaging | v1 |
| Data versioning | DataLad | large-file and reproducibility workflow | later / optional |
| Citation | CITATION.cff / CodeMeta / Zenodo | software citation and archival | v1 |
| Evaluation publishing | OSF / Registered Reports | preregistration and evaluation transparency | v1 |
| Software credit | JOSS | software paper pathway | v1+ |

## Rule of thumb

If a proposed feature bypasses the standards layer, require a strong written justification.

