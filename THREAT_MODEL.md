# Threat model

## Security posture

This project should start from a conservative security stance.

It is an agent-compatible research workflow system that may handle:

- participant-derived data
- unpublished study materials
- confidential metadata
- local files and scripts
- credentials for optional services

Treat all of those as sensitive.

## Assets

- source code
- study specifications
- participant data
- analysis outputs
- credentials and tokens
- provenance and logs
- release artifacts

## Trust boundaries

### Boundary 1: operator / lab

A deployment should be treated as belonging to one trusted lab or operator boundary.

### Boundary 2: study

Sensitive studies should be isolated from each other where feasible.

### Boundary 3: skill origin

Differentiate:

- core reviewed skills
- experimental in-repo skills
- external community skills

Do not assume equal trust across those categories.

## Primary threats

1. malicious or unsafe skills
2. prompt injection through datasets, papers, or metadata
3. accidental PII leakage into logs or reports
4. destructive filesystem or shell actions
5. silent network egress
6. dependency or supply-chain compromise
7. overstated scientific claims presented as validated output

## Core controls

- reviewed core repository only for launch
- no public skill marketplace at launch
- read-only defaults wherever possible
- explicit approval for destructive or networked actions
- dependency pinning
- deterministic demo data
- network allowlists for optional integrations
- secret material outside skill context
- signed releases where feasible
- CI checks for doc drift and basic hygiene
- clear separation of supported vs experimental skills

## Logging policy

Do not log:

- raw participant identifiers
- secrets
- absolute sensitive paths
- raw response content that could re-identify participants

Prefer structured logs with redaction.

## Incident response

If a security or privacy issue is discovered:

1. stop shipping affected workflow examples
2. document impact and scope
3. fix, test, and release
4. publish a transparent changelog entry
5. update the threat model if the issue reveals a missing control

## Launch rule

Until the security model is better tested, external skills must be treated as **untrusted** and should not be marketed as safe by default.

