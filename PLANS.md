# ExecPlan contract

Classification: **CURRENT planning contract**
Status: **PROPOSED replacement for `PLANS.md`**

This file is authoritative for execution-plan requirements and lifecycle. It does
not define product direction, runtime behaviour, architecture, or progress for a
specific task.

An ExecPlan is a version-controlled, living implementation record. It enables an
agent with no conversation history to resume substantial work safely, understand
the intended outcome and boundaries, reproduce evidence, and leave an accurate
handoff.

---

## 1. When an ExecPlan is required

Create or update an ExecPlan before substantial implementation involving any of:

- Architecture or major processing boundaries.
- Canonical identity or domain-model contracts.
- Data schemas, migrations, storage authority, or retention.
- External integrations or synchronization.
- Recommendation-affecting LLM, Agent, matching, ranking, or evaluation behaviour.
- Multiple subsystems, producers, consumers, or compatibility surfaces.
- Difficult rollback, recovery, replay, or partial-failure handling.
- New infrastructure, production resources, credentials, or material spending.
- Substantial product semantics or human approval boundaries.

A small, isolated, low-risk bug fix normally does not need a standalone plan unless
its actual risk, compatibility impact, or recovery needs justify one.

An ExecPlan organizes work already within the authorized task. It does not authorize:

- A later roadmap phase.
- A changed product or architecture decision.
- Production data writes, deployment, live scraping, or external communication.
- Access to credentials or sensitive personal information.
- An irreversible migration, destructive deletion, or authority cutover.
- Increased spending.

Those actions remain subject to [`AGENTS.md`](AGENTS.md) and explicit human
approval where required.

---

## 2. Plan location and lifecycle

Active plans live at:

```text
docs/plans/active/<task-slug>.md
```

Completed, cancelled, or superseded plans live at:

```text
docs/plans/completed/<task-slug>.md
```

Create `docs/plans/completed/` only when the first plan is ready to leave the
active collection. Do not add empty placeholder directories.

Lifecycle:

```text
Proposed
   ↓ human acceptance of objective, scope, and gates where required
Active
   ↓ implementation, evidence, validation, and documentation updates
Completed
```

Alternative terminal states:

```text
Cancelled
Superseded
```

A cancelled or superseded plan records its reason and successor, if any. It must
not imply successful delivery.

An untracked local file does not satisfy the version-controlled plan contract. The
plan must be included with the implementation changes according to the task's Git
instructions.

---

## 3. Required plan metadata

Every ExecPlan states:

- Title.
- Status: `Proposed`, `Active`, `Completed`, `Cancelled`, or
  `Superseded`.
- Classification: `PLAN`.
- Owner or responsible task.
- Created and last-updated dates.
- Starting revision, branch/worktree context, and any dirty-working-tree
  qualification.
- Related roadmap outcome, product specification, architecture section, design, or
  decision.

Do not claim a clean baseline when unrelated user changes already exist. Preserve
and identify those changes.

---

## 4. Required plan sections

An ExecPlan must be self-contained enough for a stateless agent to resume it. Mark
a section not applicable with a reason instead of silently omitting a material
consideration.

| Required section | Responsibility |
|---|---|
| Purpose / Big Picture | State the problem, why now, and observable user or system outcome. Link the relevant roadmap outcome or product specification. |
| Context and Orientation | Identify affected files/functions, current behaviour, evidence inspected, terminology, producers, consumers, and compatibility surfaces. |
| Scope | Define the exact delivery boundary. |
| Non-goals | Explicitly defer adjacent product, architecture, cleanup, and later-phase work. |
| Authority and Ownership | Identify authoritative data/doc owners, human-owned facts, and any affected Supabase/Notion/Obsidian boundary. |
| Compatibility Constraints | Identify interfaces, files, schemas, CLI/workflow paths, state, and consumer behaviour that must survive or be explicitly migrated. |
| Data, Safety, Cost, and External Effects | Identify sensitive data, secrets, production resources, paid calls, untrusted inputs, deletion, and external side effects. |
| Human Approval Gates | State exactly where work must stop for product decisions, sensitive facts, production writes, external actions, migration, cutover, spending, merge, or deployment approval. |
| Plan of Work | Explain milestones, dependency order, safe checkpoints, and why the sequence is recoverable. |
| Concrete Steps | Give actionable changes and commands with working-directory, prerequisites, and expected observations. |
| Validation and Acceptance | Define observable acceptance criteria, required unit/contract/integration/evaluation checks, expected results, actual results, and verification limits. |
| Idempotence / Failure / Recovery | Explain reruns, partial failure, data preservation, rollback/recovery, interruption, and retry behaviour, or why they are not applicable. |
| Interfaces and Dependencies | Identify contracts, external systems, configuration, credentials by variable name only, and dependent work. |
| Documentation Impact | List the exact owning documents expected to change, conditional updates, and the reason when no durable documentation changes. |
| Progress | Maintain dated completed/pending steps, blockers, and the next executable action. |
| Surprises & Discoveries | Record unexpected evidence and its effect on scope, design, risk, or validation. |
| Decision Log | Record dated task-local decisions and rationale. Link durable decisions to the owning design or ADR instead of creating a parallel architecture history. |
| Outcomes & Retrospective | At closure, record delivered behaviour, actual evidence, deviations, residual work, and lessons. |

Links supply context, but essential scope, acceptance, approval, and recovery
information must be understandable from the plan.

---

## 5. Working the plan

Before implementation:

1. Inspect Git status and identify unrelated changes.
2. Read `AGENTS.md`, `docs/current-state.md`, relevant architecture sections,
   the owning design/specification, and affected implementation/tests.
3. Confirm objective, scope, non-goals, authority, compatibility, external effects,
   and human gates.
4. Record the starting revision and current evidence.
5. Define observable acceptance and recovery before making risky changes.

During implementation:

- Update Progress, discoveries, decisions, validation, and documentation impact as
  evidence changes.
- Keep the next executable action accurate.
- Make the smallest coherent, independently verifiable change.
- Preserve working paths until their replacement is implemented, validated,
  recoverable, and approved where necessary.
- Stop at the applicable approval gate; a dry-run or payload preview is not
  permission for a real external write.
- Do not hide failures by weakening tests, schemas, evaluation fixtures, or
  acceptance criteria.
- If new evidence changes product direction, architecture, data ownership, or scope,
  stop at a safe boundary and request the smallest required human decision.

Before handoff or interruption:

- Record the exact current state, commands/results, blockers, unresolved decisions,
  and next executable action.
- Update `docs/current-state.md` when coordination or handoff truth changed.

---

## 6. Validation evidence

Validation is proportional to risk and records both positive evidence and limits.
As applicable, include:

- Unit tests for deterministic logic.
- Contract/schema tests for boundaries and compatibility.
- Integration tests for persistence and synchronization.
- Migration/backfill/replay tests, including idempotence and recovery.
- Evaluations for LLM, Agent, canonical matching, ranking, or recommendation
  behaviour.
- Security, policy, and secret-exposure checks.
- Smoke tests for user-facing commands and workflows.
- Diff inspection and affected-consumer review.
- Counts, sampled semantic parity, and explicit unknown/error cases.

Passing tests establishes only what they exercise. Do not infer live collector,
remote workflow, production integration, browser, notification, model, or
deployment health without corresponding evidence.

Record skipped or unavailable checks and why.

---

## 7. Supabase and data-migration requirements

Any plan that changes the Supabase schema, introduces a shadow write, performs a
backfill, or affects storage authority must define:

- Version-controlled migrations; no unrecorded production-dashboard schema edits.
- Current and target authority.
- Field/data ownership and affected synchronization boundaries.
- Compatibility with current JSON and active consumers.
- Idempotent migration, backfill, replay, and retry behaviour.
- Validation and semantic parity criteria.
- Environment isolation and access-policy review.
- Backup, restore, and recovery rehearsal.
- Cutover and post-cutover observation.
- Explicit approval gates for the first production write and authority cutover.

Before cutover, JSON remains authoritative. After an approved cutover, JSON is a
generated compatibility/export artifact and must not become an independent
write-authority.

---

## 8. Documentation impact

The plan identifies exact task-specific documentation updates. Use
[`docs/README.md`](docs/README.md) for general routing.

Typical routing:

| Changed truth | Owning document |
|---|---|
| Active work, blocker, verified state, or next handoff | `docs/current-state.md` |
| Verified implementation boundary | `ARCHITECTURE.md`, CURRENT |
| Accepted target direction | Owning design/ADR plus `ARCHITECTURE.md`, TARGET |
| Migration stage, temporary authority, cutover, or recovery | `ARCHITECTURE.md`, TRANSITION plus plan/runbook |
| Product phase outcome or sequence | `docs/roadmap.md` |
| Detailed product semantics | Owning product specification |
| Durable technical contract | Owning file under `docs/designs/`, executable contracts, and tests |
| User-visible setup or operation | Root `README.md` or owning guide/runbook |
| LLM/Agent/ranking quality | Owning evaluation specification and results |
| Document path, status, family, or responsibility | `docs/README.md` |

Do not update every document after every task. Update only documents whose owned
truth changed. If none changed, record `Documentation impact: none` with a reason.

---

## 9. Closing a plan

Close a delivered plan only when:

- Acceptance criteria are met or explicitly accepted with documented residual risk.
- Actual validation and verification limits are recorded.
- Human approval gates were respected and approvals are recorded where required.
- Owning documentation and handoff are current.
- Residual work is explicitly assigned, deferred, or rejected.
- Recovery information is sufficient for the delivered risk.
- The final diff has been inspected and unrelated user changes are preserved.

At closure:

1. Complete Outcomes & Retrospective.
2. Update `docs/current-state.md`.
3. Update `docs/README.md` if the plan moves or document responsibilities change.
4. Move the plan from `docs/plans/active/` to `docs/plans/completed/`.
5. Update inbound links.

Completed plans are historical execution evidence, not current architecture or
runtime documentation. Preserve their final record; make later factual corrections
explicit.

---

## 10. Knowledge boundaries

- [The roadmap](docs/roadmap.md) owns accepted phases and desired outcomes; plans
  own delivery.
- [Architecture](ARCHITECTURE.md) owns the high-level CURRENT, TARGET, and
  TRANSITION map.
- Product specifications own detailed user behaviour and acceptance semantics.
- Designs/ADRs own durable technical contracts and decisions.
- [Current state](docs/current-state.md) points to active work without copying the
  plan's progress.
- Active ExecPlans own task progress, discoveries, evidence, and task-local
  decisions.
- References remain dated evidence and must be re-verified for drift-prone CURRENT
  claims.

Do not create a parallel roadmap, architecture, decision ledger, or general debt
tracker inside an ExecPlan.

Update this contract only when planning rules or lifecycle requirements change.
Do not update it to record progress for a specific task.
