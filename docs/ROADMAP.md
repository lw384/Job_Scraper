# Job Search OS roadmap

Classification: TARGET. Authoritative for broad accepted product/engineering
direction and phase sequencing, not implementation status or execution steps.
The project evolves from its existing scraper; working behaviour remains operational
until an explicit replacement is implemented and validated.

## Phase 1 — Foundation and Data Platform

Desired outcomes:

- One canonical Job representation across collectors and downstream processing.
- Clearer processing and service responsibilities introduced where needed, without
  a cosmetic big-bang refactor.
- Existing JSON outputs, CLI entry points, and workflow compatibility throughout
  migration.
- A temporary Supabase/Postgres shadow-write migration while the existing JSON
  path remains primary, followed by storage parity validation and explicit cutover.
- After cutover, Postgres is the authoritative job store and JSON is generated
  compatibility/export output. Permanent JSON/Postgres dual-write is not the target.
- Stronger cross-source canonicalization, job identity, and deduplication.
- Reliable direct application URL resolution where possible, distinct from source
  posting identity.
- ATS-aware live-job verification with `LIVE / CLOSED / UNKNOWN` semantics.

[Architecture](../ARCHITECTURE.md#intended-storage-authority-transition) owns the
high-level storage authority transition. Exact canonical fields, database layout,
parity criteria, cutover mechanics, URL resolution, and verifier implementations
require future technical designs and substantial implementation ExecPlans.

## Phase 2 — Application Intelligence

Build on the canonical data platform to provide:

- Canonical role classification.
- Deterministic eligibility filtering before probabilistic analysis.
- Structured job-description analysis.
- Fit Score as a relatively stable measure of role fit.
- Daily Priority as a separate urgency and action-ranking measure.
- Shortlist generation.
- Notion integration for the human application workflow.

Postgres/Notion field ownership, permitted write directions, synchronization policy,
and conflict handling are unresolved until explicitly designed. This roadmap does
not imply bidirectional synchronization or Notion ownership of raw collected jobs.

## Phase 3 — Career Intelligence

Use market and application evidence to support:

- Skill normalization and taxonomy.
- Separate market-JD and applied-JD skill frequency analysis.
- Capability gaps and evidence gaps.
- Project/evidence matching and interview-story matching.
- Job-specific interview preparation.
- Weekly preparation and learning feedback loops.

## Sequencing and ownership

Establish trustworthy canonical data before adding intelligence. Application
intelligence precedes the broader career feedback capabilities. These phases are
desired outcomes, not assertions that earlier work is complete or authorization
to implement later phases during an unrelated task.

[Current state](CURRENT_STATE.md) owns the active handoff. Future product specs own
detailed capability semantics; technical designs own implementation decisions;
[ExecPlans](../PLANS.md) own bounded delivery and validation. No implementation
checklists, table definitions, scoring formulas, or deadlines are established here.

The user, or an agent explicitly authorized to change product direction, updates
this roadmap when phase outcomes, priorities, or sequencing change. Earlier phase
numbers in legacy documents are not the phases defined here; see [the catalog](README.md).
