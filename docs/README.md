# Documentation catalog

Classification: **REFERENCE / NAVIGATION**

Status: **Accepted**

Last reviewed: 2026-09-29

This file is the authoritative catalog for documentation responsibilities,
locations, lifecycle, ownership, naming, and update routing. It tells humans and
agents where durable knowledge belongs.

This file is not an additional source of product behaviour, runtime truth,
architecture, task progress, or implementation evidence. Those subjects remain
owned by the documents linked below.

---

## 1. Governing documents

These documents define repository-wide rules and remain at the repository root.

| Knowledge | Authoritative document | Classification / status | Primary owner | Update trigger |
|---|---|---|---|---|
| Agent operating rules, evidence order, approval gates, and documentation map | [`AGENTS.md`](../AGENTS.md) | CURRENT operating contract | Human-approved; Agent may draft | Repository-wide operating rules, approval gates, or stable ownership boundaries change |
| High-level system boundaries and evolution | [`ARCHITECTURE.md`](../ARCHITECTURE.md) | CURRENT / TARGET / TRANSITION | Joint; human accepts TARGET | Component, data-authority, integration, trust, deployment, or transition boundary changes |
| ExecPlan format and lifecycle | [`PLANS.md`](../PLANS.md) | CURRENT planning contract | Joint | Planning threshold, required evidence, or plan lifecycle changes |
| User setup, configuration, and usage | [root `README.md`](../README.md) | CURRENT user documentation | Joint | User-visible setup, configuration, commands, or behaviour changes |
| Documentation responsibilities and routing | [`docs/README.md`](README.md) | REFERENCE / NAVIGATION | Joint | A document or family is added, moved, renamed, reclassified, superseded, or retired |

Use [`AGENTS.md`](../AGENTS.md) to decide how to work. Use this catalog to decide
where documentation belongs.

---

## 2. Core coordination documents

| Knowledge | Authoritative document | Classification / status | Primary owner | Update trigger |
|---|---|---|---|---|
| Accepted product and engineering phases | [`roadmap.md`](roadmap.md) | TARGET | Human-approved; Agent may draft | Phase outcomes, priority, or sequencing changes |
| Current engineering handoff | [`current-state.md`](current-state.md) | CURRENT coordination | Agent-maintained; human may correct | Active work, blocker, verified state, or next milestone changes |

The roadmap does not own implementation status. The current handoff does not own
architecture, detailed task progress, or historical evidence.

---

## 3. Current technical designs

| Design | Path | Classification / status | Owns | Does not own |
|---|---|---|---|---|
| Canonical Job model | [`designs/canonical-job-model.md`](designs/canonical-job-model.md) | TARGET design / Accepted / Not yet implemented | Domain boundaries, identity, provenance, time and unknown semantics, derived-data separation, and JSON compatibility | Active task progress, physical Supabase schema, or claims that the design is implemented |

Technical designs contain durable contracts, rationale, alternatives, and unresolved
questions. Machine-readable schemas and executable contract tests own executable
field enforcement when they exist; designs explain the semantics and choices.

---

## 4. Current execution plans

| Plan | Path | Classification / status | Owns |
|---|---|---|---|
| Canonical Job foundation | [`plans/active/canonical-job-foundation.md`](plans/active/canonical-job-foundation.md) | PLAN / Active | Task scope, non-goals, progress, discoveries, validation, task-local decisions, recovery, and outcomes |

Active plans live under:

```text
docs/plans/active/<task-slug>.md
```

After all acceptance criteria and handoff work are complete, move the plan to:

```text
docs/plans/completed/<task-slug>.md
```

Create `docs/plans/completed/` only when the first plan is actually completed. Moving
a plan requires updating this catalog, `current-state.md`, and all inbound links.

---

## 5. Current guides and supporting assets

These materials help humans use or understand the project. They do not govern
runtime behaviour or override the governing documents.

| Material | Current path | Treatment |
|---|---|---|
| Agent-First engineering handbook | [`guides/Human_Software_LLM_Agent_Job_Search_OS_Agent_First_Playbook_ZH.md`](guides/Human_Software_LLM_Agent_Job_Search_OS_Agent_First_Playbook_ZH.md) | Chinese reference guide and templates. Its target examples are not implementation facts or authorization to change architecture. |
| CV-to-config prompt | [`cv-to-config-prompt.md`](cv-to-config-prompt.md) | User helper for preparing `config.json`. Loaded configuration and implementation determine actual behaviour. |
| Dashboard demo | [`triage.gif`](triage.gif) | User-facing visual asset. |
| Legacy AI triage guide | [`legacy-ai-triage.md`](legacy-ai-triage.md) | Existing legacy feature reference, not Agent instructions or a commitment to its proposed next steps. |

The CV prompt, dashboard asset, and legacy guide retain their current paths for
compatibility with existing README, script, and source references. A future
housekeeping change may move them under `guides/`, `assets/`, or
`references/legacy/`, but the move must update every inbound reference atomically.

---

## 6. Historical and point-in-time references

References preserve dated evidence and historical context. They do not govern
current behaviour, accepted direction, or active work.

| Material | Path | Treatment |
|---|---|---|
| Current repository audit at its inspection date | [`references/current-repository-audit.md`](references/current-repository-audit.md) | Point-in-time inspection evidence; re-inspect implementation before relying on drift-prone claims |
| Legacy requirements | [`references/legacy-requirements.md`](references/legacy-requirements.md) | Superseded project scope |
| Legacy Phase 0 baseline | [`references/legacy-phase-0-baseline.md`](references/legacy-phase-0-baseline.md) | Historical baseline and test evidence |
| Legacy Phase 2 personal configuration | [`references/legacy-phase-2-personal-config.md`](references/legacy-phase-2-personal-config.md) | Earlier customization milestone, unrelated to the current Application Intelligence phase |
| Historical deep dives | [`references/deep-dive/`](references/deep-dive/) | Older implementation explanations, dashboard material, and historical plans |
| Earlier tool-specific guide | [`CLAUDE.md`](../CLAUDE.md) | Historical tool guide; common repository rules are owned by `AGENTS.md` |

Old paths or phase names inside preserved historical evidence do not establish
current document authority.

---

## 7. Document families

Create a document family only with its first substantive document. Do not create
empty directories to imitate a target repository tree.

### 7.1 Families that currently exist

| Family | Path | Owns | Excludes |
|---|---|---|---|
| Technical designs | `docs/designs/` | Durable technical contracts, rationale, alternatives, unresolved choices, and accepted decisions | Live task progress, user journeys, copied schema catalogs |
| Active and completed plans | `docs/plans/` | Bounded delivery, progress, validation, discoveries, task-local decisions, recovery, and outcomes | A competing roadmap or architecture |
| Human guides | `docs/guides/` | Reusable how-to and explanatory material | Runtime truth or repository-wide operating rules |
| References | `docs/references/` | Dated audits, historical material, research evidence, and source limits | Current instructions, product authority, or active status |

### 7.2 Families created only when needed

| Future family | Path pattern | Create when | Owns |
|---|---|---|---|
| Product specifications | `docs/product-specs/<capability>.md` | A capability needs detailed user semantics, examples, exceptions, and acceptance criteria | Product behaviour and non-goals, not storage mechanics |
| Architecture decisions | `docs/decisions/ADR-NNNN-<decision>.md` | A hard-to-reverse or cross-system decision needs independent history beyond its design | Context, options, decision, consequences, and supersession |
| Runbooks | `docs/runbooks/<operation>.md` | A real recurring or high-risk operation needs verified execution and recovery instructions | Operational steps, checks, failure handling, and recovery |
| Evaluation specifications | `docs/evaluations/<capability>.md` | LLM, Agent, matching, ranking, or recommendation quality needs a durable definition of good | Datasets/slices, metrics, gates, cost, latency, and review rules |
| Generated references | `docs/generated/<artifact>` | A checked-in generator can reproduce the artifact from identified authoritative inputs | Derived output only; never hand-edited authority |

Keep invariants in `AGENTS.md`, the owning design, executable schemas, and tests
until their volume justifies a separate family. Keep task checklists and work logs
inside the active ExecPlan until a checklist is reused across multiple tasks.

---

## 8. Naming and path conventions

### 8.1 Stable root names

Repository-level entry points use conventional uppercase names:

```text
README.md
AGENTS.md
ARCHITECTURE.md
PLANS.md
```

### 8.2 Documents under `docs/`

- Use lowercase kebab-case: `current-state.md`,
  `canonical-job-model.md`.
- Use lowercase plural directory names: `designs/`, `plans/`,
  `references/`.
- Use a locale suffix for language-specific material:
  `agent-first-engineering-playbook.zh-CN.md`.
- Use `YYYY-MM-DD` only for point-in-time evidence when the date is part of its
  identity.
- Keep status in document metadata or lifecycle directories, not in names.
- Do not use `final`, `latest`, `new`, `copy`, or ungoverned `v2`
  suffixes.
- Do not create two paths for the same authoritative subject.

Existing non-conforming or compatibility paths remain valid until an explicit,
atomic rename updates all references. Do not infer that a desired naming convention
means a file has already moved.

### 8.3 Recommended document metadata

Substantive documents should make these fields clear where applicable:

```markdown
Classification: CURRENT | TARGET | PLAN | REFERENCE | GENERATED
Status: Proposed | Accepted | Active | Completed | Superseded | Rejected
Owner: Human | Agent-maintained | Joint
Last reviewed: YYYY-MM-DD
```

Not every historical reference needs retroactive metadata. Do not rewrite preserved
historical bodies merely to satisfy current style.

---

## 9. Documentation update routing

Use this table after implementation work to decide which owning document must
change. Update only documents whose owned truth changed.

| Change produced or discovered | Owning location | Required action | Human gate |
|---|---|---|---|
| Task progress, commands, discoveries, validation, or task-local decisions | Active ExecPlan under `docs/plans/active/` | Update throughout the task | Human reviews scope, acceptance, and risk decisions |
| Active task, blocker, verified state, or next handoff changed | [`current-state.md`](current-state.md) | Update the concise handoff | Human input only when a product decision or fact is needed |
| Verified implementation boundary changed | `ARCHITECTURE.md`, CURRENT | Update in the same reviewed change with implementation evidence | Review required |
| Accepted target architecture changed | Relevant design/ADR plus `ARCHITECTURE.md`, TARGET | Record rationale, acceptance, and linked target change | Explicit human acceptance |
| Migration stage, temporary authority, cutover criterion, or recovery boundary changed | `ARCHITECTURE.md`, TRANSITION plus active plan/runbook | Update transition state and evidence | Explicit approval for first production writes and authority cutover |
| Product outcome or phase sequence changed | [`roadmap.md`](roadmap.md) | Update accepted outcomes or sequencing | Human approval |
| Detailed user behaviour, examples, or acceptance semantics changed | Owning product specification, when one exists | Update spec and affected acceptance tests | Human approves product semantics |
| Durable technical contract changed | Owning file under `docs/designs/`, executable schema/contract, and tests | Update all affected authorities together | Human review for material semantics |
| User-visible setup, configuration, command, or workflow changed | Root `README.md` or an owning guide | Update instructions and verify examples/smoke path | Review required |
| Repeated or high-risk operation changed | Owning runbook, when one exists | Update steps, validation, failure, and recovery instructions | Human approval for high-risk actions |
| LLM, prompt, matching, ranking, or Agent behaviour changed | Versioned prompt/config plus owning evaluation spec and results | Re-run relevant evaluation and record cost/latency/quality evidence | Human approves business gates and risk slices |
| Point-in-time investigation completed | `docs/references/` | Add dated evidence with scope and limitations | No architecture acceptance implied |
| Document added, moved, renamed, reclassified, superseded, or retired | This catalog | Update catalog and all inbound links in the same change | Review required |
| No durable documentation truth changed | Active plan or review packet | Record `Documentation impact: none` with a reason | None beyond normal review |

This table defines general routing. It does not decide the exact files for a
particular task.

---

## 10. Task-specific documentation impact

Every substantial ExecPlan should include a task-specific documentation section:

```markdown
## Documentation impact

Update during the task:

- `docs/plans/active/<task>.md`
- `docs/current-state.md`

Update only if the owned contract changes:

- `ARCHITECTURE.md`
- `docs/designs/<owning-design>.md`
- `README.md` or an owning guide

Update if documents are added, moved, renamed, or reclassified:

- `docs/README.md`
- `AGENTS.md`, only when a major entry point or document-family path changes
```

The ExecPlan states what the current task expects to touch. The completion report
or PR records what actually changed and why.

---

## 11. Completion review

Before declaring a substantial task complete, verify:

- [ ] The active ExecPlan contains actual progress, discoveries, decisions, and
      validation results.
- [ ] `current-state.md` reflects the current handoff and next action.
- [ ] CURRENT architecture changed only where verified implementation boundaries
      changed.
- [ ] TARGET architecture changed only where the human accepted a changed direction.
- [ ] TRANSITION changed where authority, migration, cutover, or recovery changed.
- [ ] The owning technical design and executable contracts agree.
- [ ] User-facing documentation changed where setup or usage changed.
- [ ] Evaluation evidence changed where probabilistic behaviour changed.
- [ ] This catalog changed if a document moved or changed responsibility.
- [ ] Old paths were searched and no stale inbound references remain.
- [ ] If no durable documentation changed, the reason is recorded.

Passing this checklist does not replace tests, evaluations, migration rehearsal,
or required human approval.

---

## 12. Catalog maintenance

The author adding, moving, renaming, reclassifying, superseding, or retiring a
substantive document updates this catalog in the same change.

For path changes:

1. Move the file once; do not maintain parallel authoritative copies.
2. Update links in governing documents, code comments, scripts, guides, plans, and
   references where current navigation depends on them.
3. Search the repository for every old path and old filename.
4. Validate relative Markdown links and embedded asset paths.
5. Update the short documentation map in `AGENTS.md` only when a major entry point
   or family path changes.
6. Preserve historical content unless a stale current-navigation link must be
   corrected.

Detailed facts stay in their owning documents. This catalog links to them rather
than copying their content.
