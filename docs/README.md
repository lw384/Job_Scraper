# Documentation catalog

Classification: REFERENCE / navigation. This catalog locates owning documents;
it is not an additional source of product or runtime truth.

## Governing documents

| Knowledge | Home |
|---|---|
| Agent operating instructions | [AGENTS.md](../AGENTS.md) |
| High-level current and target architecture | [ARCHITECTURE.md](../ARCHITECTURE.md) |
| Execution-plan rules | [PLANS.md](../PLANS.md) |
| Current engineering coordination and handoff | [CURRENT_STATE.md](CURRENT_STATE.md) |
| Product/engineering phases and intended outcomes | [ROADMAP.md](ROADMAP.md) |
| Point-in-time repository inspection | [Repository audit](references/current-repository-audit.md) |
| Existing user setup and usage | [Root README](../README.md), verified against implementation when needed |

## Document families

Introduce a family only when its first substantive document is needed. The names
below reserve responsibilities; they do not imply that the directories exist.

| Family | Introduce when | Owns / excludes |
|---|---|---|
| `design-docs/` | A substantive technical concern needs explicit design and decisions. | Technical contracts, rationale, unresolved choices, and durable decisions. Label proposed/accepted/implemented separately; exclude live task progress and copied schema catalogs. |
| `product-specs/` | A capability needs detailed user semantics and acceptance examples. | Product behaviour and non-goals; exclude storage mechanics and implementation steps. |
| `exec-plans/` | Substantial implementation meets the [plan threshold](../PLANS.md). | Living active plans and historical closed plans; exclude a competing roadmap or architecture specification. |
| `references/` | An audit or external investigation supplies useful evidence. | Dated inspections/research with sources and limits. The existing audit is a snapshot, not rolling memory. |
| `generated/` | A checked-in generator can reproduce a useful reference from authoritative machine-readable inputs. | Derived outputs only. Identify input, generator, and regeneration command. AI-authored prose alone is not mechanically generated documentation under this contract. |

Use this catalog initially instead of separate design/product indexes. Durable
decisions live with their technical design; task-local decisions live in plans.
Machine-readable model/schema/mapping definitions should own field contracts;
designs explain semantics and choices, and generated references derive from them.
Their future formats and paths are not decided by this catalog.

## Legacy and historical material

These documents do not govern the new roadmap. Older phase numbers refer to the
earlier customization effort, not the phases in [ROADMAP.md](ROADMAP.md). They may
contain stale runtime claims; re-inspect implementation before using them.

| Material | Treatment |
|---|---|
| [Earlier requirements](requirements.md) | Superseded project scope, preserved without rewriting its historical body. |
| [Phase 0 baseline](phase-0-baseline.md) | Dated baseline evidence; its passing test report is not current test status. |
| [Phase 2 personal configuration](phase-2-personal-config.md) | Earlier configuration milestone; not Application Intelligence Phase 2. |
| [AI triage guide](AGENT_README.md) | Existing legacy feature guide, not repository agent operating instructions or a commitment to its suggested next steps. |
| [Claude guide](../CLAUDE.md) | Earlier tool guide; common operating rules are owned by AGENTS.md. |
| [Scraper deep dive](deep-dive/job-scraper-2026-04-21.md) and [session changes](deep-dive/job-scraper-changes-2026-04-21.md) | Historical explanations of older code. |
| [Dashboard deep dive](deep-dive/triage-dashboard-2026-05-27.html) | Historical dashboard explanation; older cache behaviour is not the current contract. |
| [Salary plan](deep-dive/salary-in-digests-plan.html) and [pre-audit version](deep-dive/salary-in-digests-plan.pre-audit.html) | Historical plans; not active ExecPlans under the new contract. |

[CV-to-config prompt](cv-to-config-prompt.md) remains a user helper; the actual
configuration and its loaders govern execution. [Dashboard demo](triage.gif) is
a user-facing asset. Historical prose/HTML remains REFERENCE even where an older
header calls it generated; no regeneration pipeline is established by that label.

The author adding, moving, or retiring a substantive document updates this catalog.
Keep detailed facts in their owning document and verify local links after changes.
