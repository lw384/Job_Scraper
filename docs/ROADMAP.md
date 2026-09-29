# Job Search OS roadmap

This document is authoritative for broad accepted product and engineering outcomes
and their dependency order. It does not describe implementation status, authorize
later phases, define detailed user semantics, or provide execution steps.

The project evolves from the existing Job_Scraper. Working behaviour remains
operational until a replacement is implemented, validated, recoverable, and
approved for cutover where required.

---

## Product outcome

Build a personal-first Job Search OS that:

- Turns multi-source job discovery into a small, explainable daily action queue.
- Helps the human spend time on higher-quality applications rather than maximizing
  collected-job or automated-action volume.
- Keeps application decisions and progress human-managed in Notion.
- Uses job and application evidence to produce company, role, and skill insights.
- Connects those insights to human-confirmed career evidence and learning in
  Obsidian.

The system may discover, normalize, analyse, rank, research, synchronize, and
prepare. The human owns personal facts, career direction, application decisions,
sensitive answers, external communication, and every application submission.

---

## Cross-phase boundaries

The following accepted boundaries apply throughout the roadmap:

- Establish trustworthy Canonical Job identity and provenance before dependent
  application or career intelligence.
- Apply deterministic rules before probabilistic or LLM judgement.
- Keep missing evidence as `UNKNOWN`; it is not false, ineligible, closed, or
  score zero.
- Keep job facts, candidate assessments, recommendations, and human application
  workflow state separate.
- Keep Eligibility, Fit Score, and Daily Priority separate.
- Keep job live state separate from human application state.
- Treat LLM and Agent outputs as versioned derived analysis, not source facts.
- Keep external application submission and sensitive answers behind human approval.
- Keep one authoritative owner per synchronized field.

[`ARCHITECTURE.md`](../ARCHITECTURE.md) owns the full high-level component, data
authority, trust, and transition map.

---

## Phase 1 — Foundation and Data Platform

### Desired outcomes

- One executable Canonical Job and Source Observation representation across
  collectors and downstream processing.
- Explicit provenance, time, URL-role, identity, unknown, and derived-data
  boundaries.
- Conservative identity outcomes that distinguish automatic merge, possible match,
  and separate records.
- Clearer processing and repository responsibilities introduced where needed,
  without a cosmetic big-bang rewrite.
- Existing JSON outputs, CLI entry points, dashboard, notifications, scores, and
  workflow compatibility throughout migration.
- Stronger cross-source canonicalization and deduplication.
- Reliable direct application URL resolution where possible, distinct from source
  posting identity.
- ATS-aware job verification using `LIVE / CLOSED / UNKNOWN`.
- Version-controlled Supabase Postgres schema and migration boundaries.
- Temporary Supabase shadow writes while the existing JSON path remains
  authoritative.
- Storage parity, consumer compatibility, backup, and recovery validation before
  cutover.
- Explicit human-approved cutover after which Supabase Postgres becomes
  authoritative and JSON becomes generated compatibility/export output.

Permanent JSON/Supabase dual-primary persistence is not a target outcome.

### Ownership outcome

Supabase Postgres is the accepted TARGET authority for engine-owned job facts,
source observations, canonical identity, derived analyses, recommendation history,
synchronization metadata, and audit records.

JSON remains CURRENT authority until the transition and approval criteria in
[`ARCHITECTURE.md`](../ARCHITECTURE.md#intended-storage-authority-transition)
are satisfied.

### Deferred detail

Exact canonical fields, physical database schema, migration sequence, parity
criteria, direct-URL resolution, live verifier coverage, access policies, and
recovery mechanics belong in accepted technical designs and substantial ExecPlans.

---

## Phase 2 — Application Intelligence

### Desired outcomes

- Normalized role classification.
- Deterministic eligibility evaluation before probabilistic analysis.
- Explicit separation of British-citizens-only restrictions, right to work,
  sponsorship, and security-clearance requirements.
- Structured job-description extraction with evidence and versioned analysis.
- Fit Score as a relatively stable measure of candidate-role fit.
- Daily Priority as a separate urgency and action-ranking decision.
- A capacity-controlled, explainable `Act now / Review` daily queue.
- Bounded Agent research for selected high-value or ambiguous roles, producing
  evidence rather than unsupported conclusions.
- Human review, save, skip, and application decisions.
- Notion integration for the human application workflow.
- Traceable recommendation and application-event history for later analysis.

Exact queue limits, scoring semantics, override behaviour, and acceptance examples
belong in accepted product specifications or reviewed configuration rather than
this roadmap.

### Ownership outcome

- The Job Search Engine and target Supabase store own collected job facts,
  canonical identity, derived analyses, recommendation history, synchronization
  metadata, and aggregate analytics.
- Notion is the primary human workspace for application decisions, stages, next
  actions, deadlines, outcomes, and workflow notes.
- Notion does not become the raw collected-job or canonical-fact authority.
- Each synchronized field has one owner; synchronization must not create
  uncontrolled multi-master state.

### Deferred detail

Exact Notion properties, permitted write directions, field mapping, conflict
handling, synchronization frequency, deletion/archive semantics, retries, and
recovery require a dedicated accepted integration design and ExecPlan. This
roadmap does not imply unrestricted bidirectional synchronization.

---

## Phase 3 — Career Intelligence

### Desired outcomes

- Normalized skill and role taxonomy.
- Separate analysis of the discovered-market sample and the applied-job sample.
- Company-size and business-theme analysis with visible sample and time-window
  limitations.
- Skill-frequency analysis across market, applied, interview, and outcome samples
  where evidence exists.
- Capability-gap and evidence-gap identification.
- Project/evidence matching and interview-story matching.
- Job-specific interview preparation.
- Weekly preparation and learning feedback loops.
- Explicit draft exchange from the engine to Obsidian.

### Ownership outcome

- Supabase Postgres owns engine-produced aggregate company, role, skill, and
  application-event analytics.
- Obsidian owns human-confirmed career evidence, stories, reflections, and learning
  plans.
- Agent- or LLM-authored personal material remains draft until the human approves
  it.
- The system may identify evidence gaps or propose story/learning links; it must not
  invent experiences, contributions, metrics, outcomes, feelings, or reflections.

### Deferred detail

Company identity, skill taxonomy, sampling rules, analytical windows, confidence
reporting, and Obsidian exchange format require later product/technical designs and
evaluations.

---

## Sequencing

```text
Canonical facts and provenance
        ↓
Canonical identity and compatibility
        ↓
Supabase shadow persistence and validated cutover
        ↓
Deterministic eligibility
        ↓
Structured LLM analysis and Fit
        ↓
Daily Priority and human review
        ↓
Notion application workflow
        ↓
Application and market analytics
        ↓
Human-reviewed Obsidian feedback
```

This order describes dependency, not a requirement to finish every possible Phase 1
enhancement before starting any bounded Phase 2 discovery. Any overlapping work
must preserve authority boundaries and have an independently reviewable plan.

---

## Status and execution ownership

Roadmap phases are desired outcomes, not implementation-status claims. Use:

- [`current-state.md`](current-state.md) for the active engineering handoff and
  next milestone.
- [`PLANS.md`](../PLANS.md) for ExecPlan requirements and lifecycle.
- `plans/active/` for concrete implementation progress, evidence, and recovery.
- `designs/` for durable technical contracts and decisions.
- Future product specifications for detailed user behaviour, examples, and
  acceptance semantics.
- [`docs/README.md`](README.md) for documentation ownership and routing.

An accepted later-phase outcome is not authorization to implement it during an
unrelated task.

---

## Updating this roadmap

The human owner approves changes to:

- Product outcomes.
- Phase priority or dependency order.
- Human/Software/LLM/Agent responsibility boundaries.
- High-level Supabase, Notion, or Obsidian ownership.
- Application-submission and personal-fact authority.

Agents may inspect evidence, identify conflicts, compare options, and draft changes.
They must not silently convert implementation convenience into accepted product
direction.

Update this roadmap when accepted outcomes, priorities, or sequencing change. Do
not update it for:

- Task progress or blockers.
- Function/file-level implementation steps.
- Database fields or migrations.
- Exact scoring formulas or thresholds.
- Commands and test results.
- Temporary workarounds.

Those belong in current state, product specifications, technical designs, active
ExecPlans, schemas, tests, evaluations, runbooks, or references according to
[`docs/README.md`](README.md).
