# ExecPlan contract

Classification: PLAN. Authoritative for execution-plan requirements and lifecycle,
not for product direction, current runtime behaviour, or individual task progress.

## When a plan is required

Use a version-controlled ExecPlan before substantial implementation involving:

- Architectural or processing boundaries.
- Storage authority or data migration.
- Multiple subsystems or major compatibility risk.
- New external infrastructure.
- Substantial product semantics.

A small isolated bug fix normally needs no standalone plan unless its risk or
scope warrants one. A plan records work within the authorized task; it does not
authorize additional infrastructure, external writes, or later roadmap phases.

## Document requirements

An ExecPlan must be self-contained enough for a stateless agent to resume it.
Include its title, status, scope, last update, and relevant starting revision or
working-tree qualifications. Identify evidence and reproducible commands instead
of relying on conversation history. Links supply context, but essential acceptance
criteria and recovery instructions must be understandable within the plan.

Use the following sections. Mark a section not applicable with a reason rather
than omitting important considerations silently.

| Required section | Responsibility |
|---|---|
| Purpose / Big Picture | State the problem and observable outcome, with links to the relevant roadmap outcome or product spec. |
| Context and Orientation | Identify affected files/functions, existing behaviour, evidence inspected, and terminology needed to resume. |
| Scope and Non-goals | Bound delivery and explicitly defer adjacent work. |
| Compatibility Constraints | Identify existing interfaces, data, CLI/workflow contracts, and consumer behaviour that must survive. |
| Progress | Maintain dated completed/pending steps, current blockers, and the next executable action. |
| Surprises & Discoveries | Record unexpected evidence and its effect on the work. |
| Decision Log | Record dated task-local choices and rationale; link durable decisions to their owning technical design. |
| Plan of Work | Explain the implementation sequence and dependencies. |
| Concrete Steps | Provide actionable changes and commands with working-directory and prerequisite context. |
| Validation and Acceptance | Define observable acceptance criteria, reproducible checks, expected results, and actual results with verification limits. |
| Idempotence / Failure / Recovery | Where relevant, explain reruns, partial failure, data preservation, rollback/recovery, and interruption handling. Otherwise explain why it is not applicable. |
| Interfaces and Dependencies | Identify contracts, external systems, configuration, credentials by name only, and dependent work. |
| Outcomes & Retrospective | At closure, record delivered behaviour, validation, deviations, residual work, and lessons. |

Plans are living implementation artifacts. The implementing agent updates Progress,
discoveries, decisions, and validation while work proceeds, including before a
handoff or interruption. Focus on independently verifiable outcomes. Do not claim
success from unchecked steps, unrun tests, or acceptance of an unimplemented design.

## Future lifecycle

```text
docs/exec-plans/active/<milestone>.md
        ↓
implementation and validation
        ↓
docs/exec-plans/completed/<milestone>.md
```

Create `docs/exec-plans/active/` only with the first substantive plan. Create the
completed directory when a plan closes. Do not add empty placeholders now.
An untracked local file alone does not satisfy the version-controlled contract:
include the plan with the implementation's version-controlled changes, following
the task's Git instructions.

Close a delivered plan only after acceptance criteria are met, actual validation
is recorded, owning documentation is updated, and residual work is explicitly
assigned or deferred. Move it to the completed collection and update the handoff
and catalog references that point to it.

Cancelled or superseded plans may also move to that collection, with a prominent
`CANCELLED` or `SUPERSEDED` status and reason; they must not imply successful delivery.
Completed plans are historical execution evidence, not current architecture
documentation. Preserve their final record; make later factual corrections explicit.

## Knowledge boundaries

- [The roadmap](docs/ROADMAP.md) owns phases and desired outcomes; plans own delivery.
- [Architecture](ARCHITECTURE.md) owns the high-level map; future technical designs
  own detailed contracts and durable decisions.
- [Current state](docs/CURRENT_STATE.md) points to active work without copying plan
  progress. Update it when coordination or handoff changes.
- Supporting audits/research remain dated references. Re-verify CURRENT claims.
- Do not create a parallel decision ledger or general debt tracker by default.
  Promote a durable decision to its relevant design and link it from the plan.

Update this contract when planning rules change, not to record milestone progress.
