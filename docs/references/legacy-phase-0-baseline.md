> **Historical reference — earlier phase numbering.** This is the dated baseline
> report from the earlier customization scope, not current phase direction or test
> status. Use [the current roadmap](../roadmap.md) for current phases and
> [the current engineering handoff](../current-state.md) for active coordination.

# Phase 0 Baseline Report

Baseline date: 2026-09-05  
Baseline commit: `2f294a88`  
Scope: test/dependency setup and read-only verification only; no product behaviour changed.

## Baseline status

The existing automated scraper regression suite is green and reproducible in an
isolated Python 3.12 environment. The four required Python entry modules parse and
import successfully.

This is a **qualified baseline**, rather than full end-to-end coverage: the current
tests cover the shared filtering, LinkedIn parsing/backfill, de-duplication, master
merge, work-arrangement classification, and schema fixture contract. They do not
exercise live external job-board responses, most source-specific scrapers, the
browser dashboard, notifications, GitHub Actions execution, or model behaviour.

## Reproduce the local test environment

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r tests/requirements-dev.txt
.venv/bin/python -m pytest tests/ -ra
```

The repository ignores `.venv/`. `tests/requirements-dev.txt` includes both
`pytest` and `jsonschema`, so the schema tests execute real Draft 2020-12 validation
instead of silently falling back to required-field checks.

## Current tests

Environment:

- macOS (Darwin)
- Python 3.12.12
- pytest 9.1.1
- jsonschema 4.26.0

Result:

```text
137 collected
137 passed
0 failed
0 skipped
Duration: 0.75s
```

Covered areas:

- Stable job identity and cross-source duplicate merging
- LinkedIn search-card parsing and job-description extraction
- LinkedIn partition/backfill merge, mixed phases, and cap reporting
- US location filtering, including all 50 states and international rejection cases
- `all_jobs.json` accumulation, `first_seen`, and field preservation
- Partition-key slug generation
- Job fixture validation against `schema/jobs.schema.json`
- Work-arrangement classification

## Required entry-point verification

The following files all passed both AST parsing and module import under Python 3.12:

```text
scrape_jobs.py     PASS
triage_agent.py    PASS
notify.py          PASS
eval_triage.py     PASS
```

Importing `scrape_jobs.py` currently reports that `config.json` is absent and that
`config.example.json` is being used. This is expected behaviour in this checkout.

## Current data sources and schedules

The table records workflows present in the repository. Whether a workflow is disabled
through the GitHub UI, and the values of repository variables/secrets, cannot be
determined from a local checkout.

| Source or task | Scraper mode | Declared schedule (UTC) | Runtime guard |
|---|---|---|---|
| Priority employers | `--biotech-only` currently declared | Daily 03:13 | Commits require `ENABLE_DATA_COMMITS=true` |
| LinkedIn | `--linkedin-only` | Hourly at :17, 15:00–03:00 | Commit guard; watchdog at :33 |
| Indeed | `--indeed-only` | Hourly at :47, 15:00–03:00 | Commit guard |
| ZipRecruiter | `--ziprecruiter-only` | Hourly at :27, 16:00–03:00 | Commit guard |
| Google Jobs | `--google-jobs-only` | Hourly at :37, 16:00–03:00 | Commit guard |
| HiringCafe | `--hiringcafe-only` | Hourly at :57, 16:00–03:00 | Commit guard |
| Glassdoor | `--glassdoor-only` | Hourly at :07, 16:00–03:00 | Scheduled runs require `ENABLE_GLASSDOOR_WATCHER=true` |
| USAJOBS | `--usajobs-only` | Daily 15:37 | Commit guard |
| CalCareers | `--calcareers-only` | Daily 16:07 | Commit guard |
| NEOGOV + CalOpps | two scraper modes | Daily 16:22 | Commit guard |
| CSU Careers | `--csucareers-only` | Daily 16:37 | Commit guard |
| Nightly AI triage | `triage_agent.py --limit 300` | Daily 09:00 | Needs candidate/API secrets; commit guard |
| Weekly digest | `notify.py --weekly-digest` | Monday 16:30 | Opt-in variable or manual force |
| Upstream sync | workflow-only | Monday 06:00 | Manual dispatch also available |

Manual-only or event-driven workflows also exist for the parallel LinkedIn backfill,
test suite, model evals, setup validation, notification test, and data clearing.

All data-writing scraper and triage workflows use the shared
`job-scraper-commit-push` concurrency group. `ENABLE_DATA_COMMITS` protects commits,
not the scrape itself.

## Current output contract

The canonical job schema is `schema/jobs.schema.json` (JSON Schema Draft 2020-12).
It permits additional properties for downstream enrichment.

Required fields:

```text
url          HTTP(S) canonical posting URL
title        non-empty job title
company      non-empty employer name
ats          enumerated source label
first_seen   UTC timestamp: YYYY-MM-DDTHH:MM:SSZ
```

Important optional fields include `location`, `date_posted`, `salary`, `description`,
`direct_url`, `job_type`, `is_remote`, `telework`, `work_arrangement`, salary metadata,
contact information, and `duplicate_urls`.

Per-source `*_jobs.json` files are rolling snapshots. `output/all_jobs.json` is the
30-day cumulative operational store used by the dashboard and triage agent.

Current checked-in master snapshot:

```text
438 jobs total
LinkedIn:   151
Indeed:     131
HiringCafe:  97
GoogleJobs:  27
USAJOBS:     16
NEOGOV:      15
CalOpps:       1
```

Full validation of the current 438 records found **24 existing schema violations**.
All are Google Jobs records containing `is_remote: null`; the schema accepts only a
boolean when the field is present. The existing pytest suite remains green because it
validates the fixture data, not the checked-in production snapshot.

## Existing known inconsistencies

These are baseline observations only and are deliberately not fixed in Phase 0.

1. `.github/workflows/scrape_jobs.yml` invokes `--biotech-only`, while
   `scrape_jobs.py` implements `--priority-only`. The unknown argument falls through
   to the legacy default path instead of selecting the intended priority scraper.
2. `eval_triage.py` still contains ML/biotech/security cases and expects role families
   such as `ml-ai` and `security`, while `triage_agent.py` currently instructs the
   model to use environmental/toxicology role families.
3. Some documentation says the cumulative store retains 14 days; the implementation
   uses `ALL_JOBS_PRUNE_DAYS = 30`.
4. The live master snapshot contains 24 `is_remote: null` records that violate the
   declared job schema.

## Baseline answer

If a later change breaks one of the currently covered scraper invariants, the test
suite can now detect it reproducibly. A green suite does **not** prove that every live
source, workflow, browser interaction, notification, or model evaluation still works;
those remain explicit coverage gaps for later targeted work and real-data acceptance.
