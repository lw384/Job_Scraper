# Current engineering handoff

Classification: CURRENT coordination. Authoritative only for engineering handoff,
not runtime behaviour. Re-verify implementation claims when they matter.
Last verified: 2026-09-15, local working tree; remote deployment is unverified.

## Active Phase

Phase 1 — Foundation and Data Platform, as defined by [the roadmap](ROADMAP.md).
This is the active engineering direction, not a claim that Phase 1 is implemented.

## Current Production Path

The implemented path remains JSON-based: configured collectors in
[scrape_jobs.py](../scrape_jobs.py) feed source snapshots and the cumulative
`output/all_jobs.json`; the static dashboard and notification/optional legacy AI
paths consume those outputs. See [CURRENT architecture](../ARCHITECTURE.md#current--implemented)
for responsibilities. No Postgres shadow write or cutover is implemented.

## Current Engineering State

- The governing documentation foundation is established. No active ExecPlan or
  Phase 1 technical design exists yet; absent document families are intentional.
  Historical requirements, older phase reports, and deep dives live under
  `docs/references/`; the separately named legacy AI feature guide is linked from
  [the catalog](README.md). Use those current locations rather than older names.
- Current job persistence authority remains the existing JSON path. The master is
  cumulative, while the dashboard also reads source snapshots. Target storage
  authority changes belong to [Architecture](../ARCHITECTURE.md#intended-storage-authority-transition).
- Preserve existing JSON filenames/envelopes and consumer loading, configuration
  names/semantics, source/backfill CLI flags, workflow invocation, URL-keyed scores,
  and browser-local annotations until their replacements are explicitly validated.
  Inspect affected producers/consumers; the audit is evidence, not a replacement
  for executable compatibility checks.
- Immediate focus: define the canonical Job contract in relation to current records
  and compatibility exports before implementation. No schema format or fields are
  selected by this handoff.

## Known Issues Relevant to Current Work

- The declared [single-record schema](../schema/jobs.schema.json) requires
  `first_seen`, but `save_jobs_output` writes source records while
  `_merge_into_all_jobs` timestamps master copies. `_coerce_bool` and JobSpy/Google
  normalizers can emit null `is_remote`, although the schema permits only boolean.
  [Schema tests](../tests/test_schema_validation.py) validate fixtures, not all
  persisted output. This drift matters to canonical-model design.
- Identity is consumer-specific: scraper newness/master merge, dashboard clustering,
  notification identity, and URL-keyed scores/annotations are not one shared
  contract. Inspect `scrape_jobs.py::_job_identity`, `triage.html::dedupe`, and
  `notify.py::_identity` before changing identifiers.
- The working tree contains pre-existing tracked edits and untracked material.
  `config.json` is untracked locally despite older prose calling it tracked.
  Inspect Git status before editing; remote configured search and deployment cannot
  be inferred from this checkout.

### Verified local test state

On 2026-09-15, the existing suite was rerun with Python 3.14.0, pytest 9.1.1,
and jsonschema 4.26.0 in an isolated environment, with bytecode/cache writes disabled:

```text
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/ -q --ignore=tests/local -p no:cacheprovider
187 passed; 0 failed; exit code 0
```

All six tests in [test_master_jobs_file_merge.py](../tests/test_master_jobs_file_merge.py)
also passed separately. That module now pins the scraper's clock to the fixture's
2026-08-15 reference time, so field-preservation tests do not age out with the real
date. Existing assertions and production 30-day retention semantics are unchanged.
This does not establish Python 3.11 CI, live collection, browser, delivery, or model
health. The [audit](references/current-repository-audit.md) preserves broader dated evidence.

## Next Recommended Milestone

Design the canonical Job model and its relationship to current source records,
master records, and JSON compatibility output. Identify the authoritative executable
contract and acceptance expectations without assuming a database layout.

The next agent should update this handoff when active work, blockers, or verified
state changes. Keep task progress in its ExecPlan and history in Git/closed plans;
do not expand this file into an audit, architecture specification, or issue tracker.
