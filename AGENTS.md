# Agent operating contract

Classification: CURRENT operating rules. Authoritative for how agents work here;
runtime behaviour remains owned by executable repository evidence.

## Project mission

This repository is evolving from a configuration-driven, JSON-based multi-source
job scraper into a personal Job Search OS. Make incremental, verifiable changes.
Product phases and outcomes belong in [the roadmap](docs/ROADMAP.md).

## Evidence precedence

When determining CURRENT behaviour, use this order:

```text
runtime code / loaded configuration / workflow definitions
        ↓
schemas and focused contract tests
        ↓
accepted technical designs
        ↓
current-state handoff documents
        ↓
historical audits and references
```

No prose document may override observed executable behaviour. A schema expresses
a declared contract; tests establish only what they exercise. Report discrepancies
instead of assuming that a declared contract is enforced at runtime.
Distinguish local working-tree evidence from remote deployment and service health.

## Required reading

For substantial implementation work, read progressively:

1. This file.
2. [Current handoff](docs/CURRENT_STATE.md).
3. The relevant CURRENT or TARGET section of [Architecture](ARCHITECTURE.md).
4. The active ExecPlan, if one exists and is linked from the handoff.
5. Task-specific technical designs and product specs, when they exist.
6. Affected code, configuration, workflows, schemas, and tests.

For a small bug fix, read this contract, check the handoff, then inspect the affected
implementation and tests. Load deeper documents only when the task needs them.
Use [the documentation catalog](docs/README.md) to find an owning document.

## Core invariants

These guide development; they do not claim that TARGET capabilities exist today.

- Evolve the implementation rather than rewriting it.
- Preserve working paths until an explicit replacement is implemented and validated.
- Establish canonical data before adding application or career intelligence.
- Apply deterministic rules before probabilistic or LLM judgement.
- Keep hard eligibility decisions separate from ranking; uncertainty is not proof
  of ineligibility.
- Source URLs and direct application URLs are distinct concepts, even when their
  values coincide. Do not silently substitute one identity contract for another.
- Job live state is conceptually `LIVE / CLOSED / UNKNOWN`; verification design
  and implementation remain future work.
- Fit Score measures role fit; Daily Priority measures urgency/action ranking.
- Keep storage responsibilities separate from presentation.
- Notion must not silently become the raw job system of record. Its field ownership
  and synchronization policy require explicit design.
- Permanent JSON/Postgres dual-write is not the target. Follow the migration
  authority transition in [Architecture](ARCHITECTURE.md#target--intended).
- Artifacts classified GENERATED are derived from identified machine-readable
  inputs and a reproducible generator; do not hand-edit them as authoritative prose.
  This does not reclassify today's primary JSON persistence as post-cutover exports.
- Do not refactor unrelated code for architectural cleanliness.

## Working method

Before editing:

- Inspect Git status and preserve unrelated existing changes.
- Inspect current behaviour and the related tests.
- Establish affected compatibility constraints and observable acceptance criteria.
- For substantial work, follow [the ExecPlan contract](PLANS.md).

After editing:

- Run relevant tests and checks; report failures and verification limits accurately.
- Inspect the diff and verify the acceptance criteria.
- Update owning documentation when its reality, decisions, or handoff state changes.
- Keep fixes, live scrapes, external writes, and deployment within the authorized task.

## Documentation rules

- The repository is the system of record for implementation knowledge.
- Label CURRENT, TARGET, PLAN, REFERENCE, and GENERATED scopes explicitly.
  Distinguish proposed, accepted, and implemented technical designs.
- Keep one authoritative home per subject; link rather than copying detailed facts.
- Keep this file a navigation map and operating contract.
- [Architecture](ARCHITECTURE.md) owns the high-level current/target map.
- [Plans](PLANS.md) owns execution-plan rules, not individual milestone progress.
- [Current state](docs/CURRENT_STATE.md) owns coordination and handoff only.
- [Roadmap](docs/ROADMAP.md) owns phases and desired outcomes.
- [The catalog](docs/README.md) owns navigation and document-family boundaries.
- Historical audits are dated inspection evidence, not continuously updated memory.
- Put durable decisions in the relevant design; task-local decisions stay in plans.
  Preserve history in Git, closed plans, or explicit decision records.
- Create document families only with their first substantive document; no empty
  placeholders or manually authored architecture under `docs/generated/`.
- Use English for authoritative engineering documentation; avoid parallel copies.

Update this contract when repository operating rules or navigation change, not
after every implementation task.
