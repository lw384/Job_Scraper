# Architecture map

Classification: CURRENT / TARGET, separated below. This is a high-level map,
derived from implementation evidence and accepted direction. It is not a detailed
schema, technical design, or execution plan.

## CURRENT — Implemented

Verified against the local working tree on 2026-09-15. Remote deployment, GitHub
settings, and live collector health are not established by this map.

```text
configuration → scrape_jobs.py collectors
                    ↓
        source filtering / normalization / deduplication
                    ↓
             save_jobs_output
              ├── full current result window → output/all_jobs.json
              ├── source JSON snapshots + new-job Markdown/HTML digests
              └── source-new jobs → instant notifications

source snapshots + all_jobs.json → static dashboard → browser-local state
all_jobs.json → weekly notifications
all_jobs.json → optional legacy AI triage → scores.json → dashboard / weekly digest
```

The branches are separate operations, not a transaction. The master is merged
from the current result list; it is not rebuilt by reading the saved snapshots.
Evidence: [scrape_jobs.py](scrape_jobs.py), `save_jobs_output` and
`_merge_into_all_jobs`.

| Responsibility | Current owner and evidence |
|---|---|
| Configuration | [config.json](config.json) overrides [config.example.json](config.example.json) through the scraper's import-time `_load_config` / `_deep_merge`. The dashboard and notifier have different loaders; there is no shared configuration service. |
| Scraping and processing | [scrape_jobs.py](scrape_jobs.py) owns source dispatch, requests/parsing, source-specific filters and normalization, URL/content deduplication, work-mode heuristics, persistence, and digests. These are not yet separate services. |
| JSON persistence | `_merge_into_all_jobs` maintains the cumulative JSON operational store; `save_jobs_output` overwrites source snapshots. Master retention prunes by `first_seen` at merge time using `ALL_JOBS_PRUNE_DAYS = 30`. No database persistence is implemented in the current pipeline. |
| Dashboard | [triage.html](triage.html), `SOURCES`, `loadJobs`, and `refresh`, fetches a fixed source list plus the master and optional scores, then derives browser views and deduplicates cards. Source records win exact-URL collisions, with missing discovery times filled from the master. |
| Browser persistence | `triage.html`, state initialization, `save`, `replaceJobs`, and `pruneState`, stores URL-keyed decisions, notes, stars, timelines, company blocks, theme, and a slim job cache in localStorage. Successful refresh replaces the fetched job list. Browser decisions do not write back to repository JSON or synchronize across devices. |
| Notifications | [notify.py](notify.py), `notify_new_jobs`, receives source-new jobs and uses deterministic relevance plus a notification tracker. `build_weekly_digest` reads the master and optional scores. Sending requires Pushover credentials; weekly sending is opt-in. |
| Legacy AI triage | [triage_agent.py](triage_agent.py), `load_jobs` and `main`, reads the master by default and writes URL-keyed scores using candidate inputs and an optional model backend. [eval_triage.py](eval_triage.py) provides separate legacy model evaluations. |
| Automation | [.github/workflows/](.github/workflows/) defines scheduled/manual collector runs, optional output commits, backfills, notification tasks, tests, and upstream sync. Normal writer workflows use `job-scraper-commit-push`; `ENABLE_DATA_COMMITS` gates their commits, not scraping or notification attempts. |

**LEGACY BUT STILL PRESENT:** priority-employer and US public-sector collectors,
direct curated ATS probes, and AI triage/evaluation paths remain in the repository.
The default `save_results` path is a persistence exception: it writes the older
three-key `jobs.json` envelope without master merge or instant notifications.
Evidence: `scrape_jobs.py` dispatch and `save_results`.

**CURRENTLY DISABLED / conditional:** legacy collector and AI workflows have
manual-only triggers. Glassdoor scheduling requires its opt-in variable. Some
local source query lists are empty; this is distinct from disabling their workflow.
Evidence: workflow trigger blocks, [glassdoor_watch.yml](.github/workflows/glassdoor_watch.yml),
[triage.yml](.github/workflows/triage.yml), [evals.yml](.github/workflows/evals.yml),
and current configuration.

For detailed inspection evidence, schema drift, and compatibility observations,
use the [point-in-time audit](docs/references/current-repository-audit.md).
Re-inspect the relevant implementation before relying on those observations.

## TARGET — Intended

Accepted direction; not a description of implemented capabilities:

```text
Collectors
    ↓
Canonical Job
    ↓
deterministic processing
    ↓
authoritative persistence
    ↓
application intelligence
    ↓
execution surfaces / integrations
```

These are conceptual responsibility boundaries, not a commitment to a framework,
service deployment topology, or a cosmetic restructuring of the existing scraper.
The [roadmap](docs/ROADMAP.md) owns product outcomes and phase sequencing.

### Intended storage authority transition

```text
existing JSON primary path
        ↓
temporary Postgres shadow write
        ↓
storage parity validation
        ↓
explicit cutover
        ↓
Postgres becomes authoritative job store
        ↓
JSON becomes generated compatibility/export artifacts
```

Permanent JSON/Postgres dual-write is not the target architecture.
Supabase/Postgres is the intended long-term persistence platform, not an existing
dependency. Preserve JSON/CLI/workflow compatibility during the transition.

Future technical designs must decide the canonical model and its executable owner,
physical database schema, lifecycle and identity contracts, parity criteria,
cutover/recovery mechanics, direct URL resolution, and ATS verification details.
Postgres/Notion field ownership and synchronization policy are also undecided.
No tables, fields, thresholds, or integration ownership rules are established here.

Update CURRENT when implemented boundaries change and are verified. Update TARGET
when accepted direction changes; link substantive future designs from the
[documentation catalog](docs/README.md) rather than duplicating their details here.
