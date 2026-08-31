# External gate intake template — remote-only

This file is an intake contract, not evidence and not a gate-closing decision. The candidate release has eight external gates open. The acceptance rules below implement the Master Plan V3 claim boundary.

## Storage boundary

- Private or transaction-sensitive documents may be stored only in a controlled Google Drive location supplied by the user or counterparty.
- This public GitHub repository stores only redacted metadata, document identifiers, verifier notes and cryptographic hashes. Do not commit customer invoices, account numbers, PII, credentials, executed contracts, private technical reports, hidden truth or proprietary raw data.
- Do not download or stage project data in the desktop workspace. Any future validation must run in memory on a remote runner or against a controlled Drive copy.
- A hash or public comparator is provenance, not proof of applicability.

## Two-level intake

- `validation/EXTERNAL_GATE_INTAKE.csv` is the gate-level register: one planning row for each EXT-001–EXT-008.
- `validation/EXTERNAL_GATE_SUBMISSIONS.csv` is the submission-metadata register. It is intentionally empty until a real evidence bundle is supplied. Add one row per submitted evidence bundle; never add raw document contents.
- `.github/workflows/external-gate-validation.yml` runs `scripts/validate_external_gate_metadata.py` remotely and fails closed on malformed or unsupported closure metadata.

## Required submission record

Use this exact header in `validation/EXTERNAL_GATE_SUBMISSIONS.csv`:

```text
gate_id,document_type,issuer_or_counterparty,document_date,effective_date,applicability_scope,redaction_status,drive_file_id_or_controlled_link,github_metadata_commit,sha256,verifier,verification_date,model_update_required,status,notes
```

A gate may move from OPEN to CLOSED only when the required evidence is directly applicable, independently checked, reconciled to model inputs, and recorded in the gate tracker. A document marked draft, indicative, comparator-only, or preparation/readiness evidence does not close a transaction gate.

## Gate-specific acceptance

| Gate | Minimum evidence to submit | Acceptance test before closing |
|---|---|---|
| EXT-001 Regulatory/billing | Current billed invoice or written utility/Electricity Authority confirmation for the modeled customer class | Invoice/effective date and customer class are explicit; legal-effective and billed-effective statuses remain separate; tariff mapping and manifest are rerun |
| EXT-002 Tax | Written Vietnam tax-counsel memo covering effective tax stack and the 28-Aug-2026 draft | Counsel identifies effective rules, transaction applicability and model changes; tax register, model and QA are rerun |
| EXT-003 Foreign borrowing/legal | Transaction-specific legal memo covering offshore borrowing, registration/reporting, security and enforceability | Actual borrower/security structure is named; legal checklist is approved; affected debt/legal inputs are reconciled |
| EXT-004 Independent model review | Independent reviewer report covering logic, formulas, inputs, controls, limitations and change log | Reviewer findings are closed or accepted with actions; no self-certification; release controls are rerun |
| EXT-005 Technical/site/bankable P90 | Third-party yield, roof/site rights, structural, grid, E&S/HSE and bankable P90 pack for selected projects | Evidence covers each selected project and debt/PPA tenor; P90 and site assumptions reconcile to the model |
| EXT-006 Executed PPA/security | Executed or near-final PPA plus direct agreement, security, insurance, termination and step-in package | Legal/lender review accepts enforceability; key commercial terms reconcile to the model |
| EXT-007 Lender/reserves/hedging | Indicative lender term sheet and approved reserve, covenant, security and hedge requirements | Terms reconcile to debt sizing, DSRA/reserve waterfall, covenant and hedge assumptions |
| EXT-008 Sponsor/IC hurdle | Approved sponsor hurdle and IC decision for the negative-base-NPV case | Decision records reprice, CAPEX reduction, structure change or reject; approved structure is rerun and reconciled |

## Status vocabulary

Use only `OPEN`, `SUBMITTED`, `UNDER_REVIEW`, `CLOSED` or `REJECTED`. `CLOSED` requires a reviewer, verification date and an updated gate-tracker row. Until then, the release remains `candidate`, `PASS_WITH_LIMITATIONS` and `recruiter_ready=false`.
