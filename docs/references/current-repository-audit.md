# Current repository audit

Audit date: 2026-09-15. This records the **local working tree**, with HEAD at `2f294a88b6942bbe21283568ea16dc4476dffed9`. It is not a claim about the deployed branch or live GitHub settings. Before this audit, `git status --short` showed 25 modified tracked files, 8 untracked files, and no staged changes. In particular, `config.json` was untracked, despite tracking claims in `README.md` and `CLAUDE.md`. Existing output files were tracked even though `.gitignore` excludes new files under `output/`. Evidence: repository tree, `git status`, `git ls-files`, `.gitignore`.

Status labels used throughout:

- **CURRENT**: implemented behaviour in the inspected working tree.
- **LEGACY BUT STILL PRESENT**: retained implementation or data whose older purpose remains visible; it can still execute when invoked.
- **CURRENTLY DISABLED**: a specific automatic trigger, query list, or option is inactive in the inspected files. This does not establish the state of remote repository variables.
- **UNKNOWN / NEEDS VERIFICATION**: cannot be established from local code, local data, and the test run.

## Architecture and data flow — CURRENT

The repository contains four job-pipeline Python entry points and an unrelated root `test.py` utility, a standalone HTML/JavaScript dashboard, JSON configuration and schema files, shell setup helpers, 21 workflow YAML files, tests and fixtures, documentation, and generated output. There is no application server or database implementation in these paths. The dashboard fetches relative static files; setup code requests GitHub Pages hosting from `main`, repository root. Evidence: `scrape_jobs.py`, `notify.py`, `triage_agent.py`, `eval_triage.py`, `test.py`, `triage.html::loadJobs`, `scripts/setup.sh`.

The normal collector path is:

1. A watcher invokes a source-specific flag in `scrape_jobs.py::__main__`.
2. The selected collector queries a board and constructs job dictionaries, applying source-specific title, location, and date rules.
3. A `save_*_results` wrapper calls `save_jobs_output`, which filters excluded employers, derives work mode, compares identities with the previous source snapshot, merges the **full current source result list** into the master, and invokes instant notifications with the source's new jobs.
4. `save_jobs_output` overwrites the source JSON and writes Markdown/HTML digests containing only new jobs.
5. The workflow optionally stages and pushes output to Git, controlled by `vars.ENABLE_DATA_COMMITS == 'true'`.
6. `triage.html::refresh` fetches configuration, optional scoring inputs, the fixed source list, and the master, then derives a browser view and saves local state.

Master accumulation and notifications are individually wrapped in broad exception handlers in `save_jobs_output`; their failures are logged as non-fatal and the source output path continues. Source files and master updates are separate writes, not a transaction. Evidence: `scrape_jobs.py::save_jobs_output`.

**LEGACY BUT STILL PRESENT:** invoking `scrape_jobs.py` without a recognized collector flag runs only the direct curated-employer sweep, target-location filter, and 24-hour freshness filter, then `save_results`. `save_results` writes `jobs.json/.md/.html` without master accumulation, instant notifications, or `new_jobs`/`new_count`. `CURATED_EMPLOYERS` is currently empty, so this default sweep yields no jobs. The flag router uses membership checks in `sys.argv`, rather than a parser that rejects unknown flags. Evidence: `scrape_jobs.py::__main__`, `scrape_curated_employers`, `save_results`.

## Configuration loading — CURRENT

`scrape_jobs.py::_load_config` reads files beside the script at import time. It recursively merges `config.json` over `config.example.json`; dictionaries merge by key and other values, including lists, replace the base value. Missing or unreadable personal configuration falls back to a non-empty usable example. If the personal file cannot be loaded and the example is also empty/unusable, it exits. A usable personal file can be used alone when the example is unavailable. `_read_json` catches missing files, JSON syntax errors, and filesystem errors, but does not validate JSON structure or configuration types. Evidence: `_read_json`, `_deep_merge`, `_load_config`, module-level `CONFIG`.

There are two distinct lookup semantics: `_cfg` substitutes the supplied default for `None`, empty strings, lists, or dictionaries; `_cfg_allow_empty` preserves explicit emptiness and substitutes only for absent keys or `None`. Glassdoor, ZipRecruiter, Google Cartesian query settings, and HiringCafe use the latter for some source settings. The deep merge happens first, so an example key may prevent a subsequent source fallback from being reached. Evidence: `scrape_jobs.py::_cfg`, `_cfg_allow_empty`, source constants near `INDEED_GEOS` and `HIRINGCAFE_SEARCH_TERMS`.

The local personal file supplies Ivy / Wei branding, 17 positive role phrases, UK-primary geography and international-remote discovery settings. `search_scope`, `skills`, and `negative_domains` are recorded metadata: the inspected collectors, notifier, and dashboard do not translate them into search queries or scoring rules. Execution uses the separate `keywords`, `search_terms`, `locations`, and `location_filter` settings. Hard title and employer exclusion lists and fuzzy keyword lists are empty in the local configuration. Evidence: `config.json`, `config.example.json`, `scrape_jobs.py` configuration lookups, `notify.py::_fit`, `triage.html::applyConfig`.

The components do **not** share one configuration loader:

- `notify.py::_load_config` reads only `config.json`, returning `{}` on missing/invalid JSON. Its `CONFIG_EXAMPLE_PATH` constant is unused. `_min_fit` reads `NOTIFY_MIN_FIT` from the environment, defaulting to 75; `config.json::notify.min_fit` is not consumed.
- `triage.html::refresh` fetches only `config.json`; a missing/invalid response leaves current/default browser settings. It does not fetch or deep-merge `config.example.json`. `applyConfig` updates branding, ordered role regexes, priority-topic regexes, and employer exclusions. An empty role-category list does not clear previously loaded categories during a subsequent refresh.
- `triage_agent.py::_read_first` loads candidate profile/resume from environment variables, or root-level Markdown/text files; it does not consume the search configuration.

Optional deterministic scoring also differs by consumer. `notify.py::_scoring_profile` reads the first existing personal/example scoring file, repairs regex escapes, compiles rules, and caches the result. An invalid existing personal file falls back to built-in empty rules, not to the example. `triage.html::loadScoringProfile` fetches only the personal scoring file. No `scoring_profile.json` exists locally; `scoring_profile.example.json` has empty rule lists. Consequently the inspected fallback scoring rules yield zero fit. The notifier's example multiplier is 1, while the dashboard's built-in multiplier is 1.6; empty rules make that difference immaterial to the present default scores.

For JobSpy proxies and user-agent settings, non-empty configuration takes precedence over environment fallback (`_jobspy_proxies`, `_jobspy_user_agent`). Google provider credentials likewise use non-empty configuration before environment values (`_google_jobs_secret`). The local credential fields are empty. Whether the remote secrets are populated is **UNKNOWN / NEEDS VERIFICATION**.

## Collectors and scraper responsibilities

| Collector | Classification in this working tree | Implemented path and scope |
|---|---|---|
| LinkedIn | CURRENT; query lists populated | `scrape_linkedin_recent` uses the public guest search endpoint, 1-hour lookback, 11 terms × 2 locations, up to 100 cards per term/location in steps of 10. It applies `role_is_relevant`, target-location filtering, and posting enrichment. |
| Indeed | CURRENT; query lists populated | `scrape_indeed_recent` → `_scrape_jobspy_board`: 8 terms × 5 UK locations, 24-hour request window, normally 50 requested results per query. |
| Glassdoor | CURRENT implementation; scheduling conditionally enabled | `scrape_glassdoor_recent` uses JobSpy, 8 terms × 2 UK locations, 24 hours. Scheduled workflow jobs require `ENABLE_GLASSDOOR_WATCHER == 'true'`; manual dispatch bypasses that condition. Remote variable value is unknown. |
| Google Jobs | CURRENT; exact queries populated | `scrape_google_jobs_recent` uses 14 paired query/location/country entries, requesting 30 JobSpy results per query. Exact query strings take precedence over empty Cartesian term/location lists. |
| ZipRecruiter | CURRENTLY DISABLED discovery by local empty term/location lists; scheduled workflow remains present | `scrape_ziprecruiter_recent` uses JobSpy. With the installed dependency and no queries, the zero-row guard returns the previous snapshot. |
| HiringCafe | CURRENTLY DISABLED discovery by local empty term list; scheduled workflow remains present | `_hiringcafe_ssr_hits` reads `__NEXT_DATA__` from `/jobs/<term-slug>` pages, up to 3 pages per term. No configured location list is used in this collector. Its current route's actual geographic coverage is unknown. |
| Priority employers | LEGACY BUT STILL PRESENT; automatic scheduling disabled and local allowlist empty | `--priority-only` combines curated direct ATS probes with `scrape_linkedin_priority` using a 24-hour LinkedIn query window. Deduplication here uses company/title only. Empty allowlist does not short-circuit the LinkedIn search itself. |
| Greenhouse / Workday direct probes | LEGACY BUT STILL PRESENT; CURRENTLY DISABLED by empty `CURATED_EMPLOYERS` | `probe_curated_greenhouse` fetches board JSON and title-filters. `probe_curated_workday` POSTs per configured term, dedupes external paths, and uses configured fallback location for missing or summarized multiple locations. Workday terms are also empty locally. |
| CalCareers | LEGACY BUT STILL PRESENT; manual-only workflow and empty local search terms | `scrape_calcareers_recent` seeds cookie/viewstate state and POSTs hardcoded ASP.NET search field/control names, parses results, and fetches work-location/telework/type details. It has no shared target-location post-filter. |
| USAJOBS | LEGACY BUT STILL PRESENT; manual-only workflow and empty local search terms | `scrape_usajobs_recent` seeds a session even before its term loop, POSTs public website search requests, reads page 1 with 50 requested results per term, and extracts salary/open date. It has no shared target-location post-filter. |
| GovernmentJobs / NEOGOV | LEGACY BUT STILL PRESENT; manual-only workflow and empty local terms | `scrape_governmentjobs_recent` parses up to 2 HTML pages per term, requests a 21-day window, and uses the current configured target-location predicate. Comments/logs still say CA/OR; the code is configuration-driven. |
| CalOpps | LEGACY BUT STILL PRESENT; automatic scheduling disabled | `scrape_calopps_recent` scans up to 10 listing pages, title-filters, and fetches salary per matching posting. There is no separate empty source-term switch or target-location filter. Manual dispatch can still collect matching California roles. |
| CSU Careers | LEGACY BUT STILL PRESENT; automatic scheduling disabled | `scrape_csucareers_recent` scans PageUp listings, up to 30 pages × 100 items, tries curl then urllib, and matches configured keywords against title **or summary** via `text_matches_keywords`. It stores summary description and closing date; there is no shared target-location filter. |

`_build_title_re` matches single-token terms at word boundaries, while multi-word or ampersand-containing phrases retain substring matching. `title_matches_keywords` requires an include match and no exclusion match. `role_is_relevant` uses the exact matcher when fuzzy lists are empty; fuzzy mode is enabled only when both seniority and domain lists are populated. Evidence: `scrape_jobs.py::_build_title_re`, `title_matches_keywords`, `role_is_relevant`.

`is_target_location` normalizes punctuation/separators and matches complete configured words/phrases, avoiding an incidental `UK` match inside `Phuket`. A match on `Remote`, including `Remote — US only`, is retained for discovery; this does not establish permitted employment geography. This filter is used by LinkedIn and NEOGOV paths, but is not a universal post-filter for every collector. Evidence: `_normalized_location`, `_location_term_matches`, `is_target_location`, collector callers, `tests/test_location_filter_us_states.py`.

The scraper also owns request delays/retries, parsing, normalization, salary extraction, description truncation, source digests, and master accumulation. LinkedIn posting descriptions are capped at 12,000 characters; JobSpy and related normalizers generally cap descriptions at 6,000. Work modes are string heuristics: generic `remote` becomes `Remote in-state eligible`, `hybrid` becomes `Telecommute eligible`, and explicit out-of-state text takes precedence. These labels are not verified eligibility decisions. Evidence: `fetch`, `_enrich_linkedin_postings`, `_linkedin_description_from_page`, `_ingest_jobspy_df`, `JOBSPY_JD_MAX_CHARS`, `classify_work_arrangement`.

Zero-data preservation is implemented for recent LinkedIn, JobSpy boards, Google Jobs, HiringCafe, and several legacy collectors. Its conditions differ by source; successful raw data with no title matches can produce a genuinely empty snapshot, while zero raw data often reuses old jobs. CSU also preserves previous jobs when its scan is marked incomplete. Missing JobSpy takes an earlier return of `[]`, before snapshot preservation or Google API fallback. Evidence: `scrape_linkedin_recent`, `_scrape_jobspy_board`, `scrape_google_jobs_recent`, `scrape_hiringcafe_recent`, legacy collector functions.

Google's primary JobSpy call receives the exact `google_search_term`; locale objects are used by fallback providers. With explicit queries, `_google_jobs_query_contexts` does not inject an hours/days phrase, so `--google-jobs-backfill` does not change those query strings. Fallback tries SerpApi then Oxylabs only after zero primary raw rows and stops on a provider's non-zero raw count, even if no rows survive filtering. Evidence: `_google_jobs_query_contexts`, `scrape_google_jobs_recent`, `_scrape_google_jobs_api_fallback`.

## JSON persistence and 30-day retention — CURRENT

| File family | Current write shape / purpose | Producer and readers |
|---|---|---|
| `output/<source>_jobs.json`, priority `output/jobs.json` | Normally `{scraped_at,total,new_count,jobs,new_jobs}`; overwritten per run, pretty-printed UTF-8 | `save_jobs_output`; dashboard, previous-snapshot guards and identity comparisons |
| `output/all_jobs.json` | `{updated_at,jobs}`; compact cumulative operational store | `_merge_into_all_jobs`; dashboard, AI agent, weekly digest |
| `output/scores.json` | `{scores,...}` with raw posting URLs as keys; top-level model/time metadata during scoring | `triage_agent.py::main`; dashboard and weekly digest; absent locally |
| `output/notified.json` | `{ids:[...]}`; normalized company/title identities, last 600 retained | `notify.py::_load_notified`, `_save_notified` |
| `output/workflow_runs.jsonl` | Append-only JSON lines with workflow, timestamp, job count, run ID and attempt | Inline watcher/backfill workflow steps; no dashboard reader |
| LinkedIn temporary artifacts | Term/partition metadata and `jobs`, matrix entries | LinkedIn CLI backfill branches and `linkedin_backfill.yml` |

`save_results` is the retained three-key source-shape exception, and the local `output/jobs.json` has that shape. The schema describes a **single job**, not any of these envelopes. Evidence: `scrape_jobs.py::save_results`, `schema/jobs.schema.json`, output inspection.

`_merge_into_all_jobs` dedupes the existing master first, merges current input, stamps newly added copies with `first_seen` as `YYYY-MM-DDTHH:MM:SSZ`, then prunes entries whose `first_seen` string is earlier than the UTC cutoff 30 days before the run. It sorts retained records by `first_seen` descending. Existing records are not given a new timestamp when seen again. Missing `first_seen` uses the current stamp for the retention comparison but is not repaired onto the old record. Comparison is lexical; no timestamp validation occurs here. Evidence: `scrape_jobs.py::_merge_into_all_jobs`, `ALL_JOBS_PRUNE_DAYS`.

Retention runs only when this merge executes. It measures discovery time, not posting date, expiry, or last successful observation. There is no live-posting deletion check, bookmark exemption, or independently scheduled master pruner. Backfills assign current discovery time even to historical postings. The returned added count is calculated before pruning. Evidence: `_merge_into_all_jobs`, backfill branches, workflow files.

The source snapshots have collector-specific request windows, not the master's retention policy. Preserved snapshots may keep stale jobs and receive a fresh `scraped_at` when saved again. Neither that timestamp nor the workflow log establishes fresh upstream data. Evidence: zero-data guards and `save_jobs_output`.

### Observed generated data, unchanged

Read-only inspection found the following local snapshot counts:

| Output JSON | Jobs | Stored time |
|---|---:|---|
| `all_jobs.json` | 438 | 2026-09-05 20:55 UTC |
| `calcareers_jobs.json` | 15 | 2026-09-05 18:13 UTC |
| `google_jobs.json` | 4 | 2026-09-05 20:42 UTC |
| `governmentjobs_jobs.json` | 14 | 2026-09-05 18:20 UTC |
| `hiringcafe_jobs.json` | 18 | 2026-09-05 20:55 UTC |
| `indeed_jobs.json` | 6 | 2026-09-05 19:35 UTC |
| `usajobs_jobs.json` | 9 | 2026-09-05 17:32 UTC |
| `jobs.json`, LinkedIn, ZipRecruiter, CalOpps, CSU snapshots | 0 each | 2026-09-05, differing times |
| `glassdoor_jobs.json` | 0 | 2026-06-20 19:10 UTC |

The master is 2,067,925 bytes. Its source labels are LinkedIn 151, Indeed 131, HiringCafe 97, GoogleJobs 27, USAJOBS 16, NEOGOV 15, and CalOpps 1. All 438 have `first_seen`; the range is August 6 through September 5. At audit time, 135 are older than the current 30-day cutoff. That is consistent with pruning occurring during writes rather than continuously. `notified.json` holds 23 identities; `workflow_runs.jsonl` has 3,478 lines, ending September 5. Evidence: the named output files, read-only JSON parsing.

**LEGACY BUT STILL PRESENT:** the output includes environmental/toxicology roles and digests branded California/Oregon/Australia. Those artifacts do not demonstrate the present UK/AI/software configuration working. Their generation provenance and why updates stopped after September 5 are **UNKNOWN / NEEDS VERIFICATION**. Representative evidence: `output/all_jobs.json`, `output/hiringcafe_jobs.json`, `output/jobs.md/.html`, `output/google_jobs.md/.html`, `output/governmentjobs_jobs.md`.

## Deduplication — CURRENT

There are separate identity contracts:

- Source newness: `save_jobs_output` compares `_job_identity(url)` only against the previous snapshot's `jobs`. A posting absent from that snapshot can be marked new even when already in the master. This comparison does not itself collapse duplicate rows within the current input list.
- Master: `_dedupe_master_jobs` and `_merge_into_all_jobs` first use exact URL/normalized identity indexes, including `duplicate_urls`, then `_same_job` heuristics.
- Notifications: `notify.py::_identity` removes non-alphanumeric characters from company and title and combines them. It ignores URL, location, and source.
- Dashboard: `loadJobs` first unions exact URLs in fixed source order; `dedupe` then performs transitive pairwise clustering using normalized URLs and content heuristics.

`_job_identity` recognizes numeric LinkedIn view paths, Indeed `jk`, ZipRecruiter `lvk`/`jid`, Greenhouse `gh_jid`, selected ATS path IDs, Talent `id`, and Glassdoor `jl`. Generic fallback lowercases host/decoded path and removes query/trailing slash. It does not include `direct_url`. Important consequence: CalCareers URLs differing only by `JobControlId` receive the same generic identity. Slugged LinkedIn paths such as the one in `output/google_jobs.json` do not use the numeric LinkedIn branch. Evidence: `scrape_jobs.py::_job_identity`, `_job_urls`; dashboard analogue `triage.html::_jobKey`.

Content matching requires normalized company agreement, similar title, and location overlap; when either location is missing, substantial description overlap can substitute. Title matching accepts identical normalized tokens, Jaccard similarity ≥0.86 with at least two shared tokens, or certain level-only extra tokens. Description matching uses the first 3,000 characters, requires at least 220 characters each, and Jaccard similarity ≥0.82. Location stopwords still include California/CA/US vocabulary. Evidence: `_company_match`, `_title_match`, `_location_overlap`, `_description_overlap`, `_same_job`.

The master keeps the first retained record's URL, employer/title, existing discovery time, and arbitrary existing downstream fields. `_merge_duplicate_job` fills only missing description/salary and a selected set of missing auxiliary fields, then accumulates sorted alternate URLs. It does not refresh non-empty existing descriptions/salaries, merge all arbitrary incoming metadata, or transfer incoming downstream tags onto an existing record. Its truthiness checks skip incoming `is_remote=False`. Retention can still delete the surviving tagged record. Evidence: `_merge_duplicate_job`, `_dedupe_master_jobs`, `_merge_into_all_jobs`, `tests/test_master_jobs_file_merge.py`.

## Dashboard and localStorage — CURRENT

`triage.html::SOURCES` explicitly lists 12 source snapshots plus `all_jobs.json`. It does not discover arbitrary files. `loadJobs` cache-busts requests, tolerates individual source failures and optional missing scores, and errors when every source request fails. Per-source versions win exact URL collisions; only missing `first_seen` is backfilled from the master. The resulting union feeds Browse, Best fit, and Map alike. A partial successful refresh does not preserve cached jobs belonging solely to failed sources. Evidence: `SOURCES`, `loadJobs`, `refresh`, `replaceJobs`.

The dashboard derives ordered title-role buckets, seniority, source, sector, work mode, fit score, and salary fields in `enrich`. It offers source/role/seniority/work/sector/status/date/search/salary/score/star filters, company and role charts, a salary histogram, and a map. Best fit ranks optional non-error agent scores before deterministic fit fallback. Browse can sort by fit, freshness, or location. The sort labelled “Time posted” uses `jobFreshMs`, which prefers discovery time; day filters use posting dates, while the sub-day filter prefers discovery time. Evidence: `enrich`, classifiers, `matchesFilters`, `rankScore`, `sortJobs`, `jobFreshMs`, `renderJobs`.

Browser state is stored under `jobTriage:v3`, with theme under `jobTriage:theme`. State contains a slim job cache, URL-keyed triage decisions, notes, user stars, timelines, blocked companies, theme, and last-load metadata. `save` strips description and underscore-prefixed derived job fields. Filters, view/sort mode, selected URLs, and focus are initialized in memory and are not persisted as those settings. Evidence: state initialization, `slimJob`, `save`, `filters`, `viewMode`, `selectedUrls`.

On a successful refresh, `replaceJobs` replaces the cached job list with fetched jobs. `pruneState` then removes untriaged stale jobs older than 30 days by freshness and untriaged excluded employers; unknown dates are retained. Any truthy triage decision exempts an incoming job from this browser prune, but does not restore jobs absent from fetched files. Orphan triage decisions remain; notes/stars/timelines are deleted only when the URL is neither live nor triaged. There is no server write-back, cross-device synchronization, or repository update for those browser decisions. Evidence: `refresh`, `replaceJobs`, `pruneState`, `save`, dashboard fetch/event handlers.

Status actions include saved, applied, interview, offer, dismissed, and irrelevant; toggling the same action returns a job to untriaged. `applyTriage` writes decisions across duplicate URLs. Cluster consolidation uses priority values only for applied, saved, irrelevant, and dismissed; interview/offer are missing from `TRIAGE_PRIORITY`. Notes, stars, and timelines are displayed by the chosen primary URL and are not generally merged across a cluster. Evidence: `applyTriage`, `_mergeCluster`, `TRIAGE_PRIORITY`, `jobNote`, timeline/rating handlers.

`computeFit` uses title-weighted rules plus company/description/agent rationale and browser-specific penalties learned from irrelevant titles. It treats an empty signature list as satisfying the signature requirement; `notify.py::_fit` does not. The notifier lacks the browser learning penalty and agent-rationale input. Thus these scorers are related implementations, not identical contracts.

Salary parsing annualizes dollar-oriented text from salary/title/description and uses magnitude heuristics; it does not convert `salary_currency` or establish exchange rates. JobSpy's `format_salary` also formats amounts with `$` regardless of stored currency. Map geocoding uses a static table concentrated on US/Australian locations and regional fallbacks; unmatched locations, including UK/China locations absent from the table, join a “Remote / Statewide” bucket. Leaflet loads from unpkg and tiles from OpenStreetMap. Evidence: `triage.html::parseSalary`, `_parseOnePay`, `CITY_COORDS`, `geocodeJob`, `renderMap`; `scrape_jobs.py::format_salary`.

CSV export downloads visible jobs with local status/notes and scoring fields. Packet actions copy an application-materials prompt for the user to combine with a CV; they do not invoke an LLM or send applications. “Clear jobs” opens the workflow page; it does not clear localStorage. Evidence: `exportVisibleCsv`, `applicationPacket`, `copy`, header link and event handlers.

## Notifications — CURRENT implementation, partly disabled locally

`save_jobs_output` calls `notify_new_jobs` for source-new jobs. Without both Pushover environment credentials, it returns immediately. Relevance is priority-topic match or deterministic score meeting `_min_fit`; instant notifications do not read agent scores. However, `notify.py::STAR_TERMS` is empty and never populated from configuration, so configured dashboard priority topics currently do not create notifier stars. No local scoring profile exists and the example rules are empty, so default fit cannot meet the default 75 threshold. Evidence: `notify.py::STAR_TERMS`, `_stars`, `_fit`, relevance, `_min_fit`, `notify_new_jobs`.

Relevant identities are appended to the tracker **before** delivery. The function sorts starred/high-fit jobs, attempts at most 8 individual pushes, then one overflow summary. It saves identities for failed sends and summarized jobs too; delivery return values do not change that tracking. Keeping only the last 600 identities permits eventual repeats. There is no durable retry queue. Evidence: `notify_new_jobs`, `MAX_PUSHES_PER_RUN`, `_save_notified`, `send_pushover`.

Weekly digest sending is **CURRENTLY DISABLED in local configuration** (`notify.weekly_digest.enabled=false`), with environment opt-in or manual force overrides supported. The workflow is still scheduled. `build_weekly_digest` selects master jobs by parsed `first_seen`, summarizes salary bands/employers, and ranks up to three distinct company/title roles using valid integer agent scores when available, deterministic fallback otherwise. It does not use browser triage or local browser learning. `--dry-run` prints without credentials or sending. Evidence: `notify.py::_weekly_digest_enabled`, `_recent_jobs`, `_score_job`, `_standout_lines`, `build_weekly_digest`, `send_weekly_digest`; `.github/workflows/weekly_digest.yml`.

The default dashboard URL is derived from `GITHUB_REPOSITORY`, or relative `triage.html` locally; the weekly digest supports `DASHBOARD_URL` override. `notify.py` without arguments sends a test notification, as does `--test`. Actual remote opt-in settings and delivery are **UNKNOWN / NEEDS VERIFICATION**; no notification was sent during this audit.

## Legacy AI triage — LEGACY BUT STILL PRESENT

`triage_agent.py` defaults to 50 roles locally; its manual workflow invokes `--limit 300`. It prefers the master, with fallback/`--from-files` union limited to `jobs.json`, `linkedin_jobs.json`, and `indeed_jobs.json`. Master loading itself does not perform another dedupe. Candidate profile is required; resume is optional. Environment values precede `candidate_profile.md`, `resume.md`, and `resume.txt`. Evidence: `load_jobs`, `_read_first`, `main`, `.github/workflows/triage.yml`.

Unscored jobs and stored error verdicts are selected by raw URL and sorted lexically by posting-date text. `--since` uses a lexical first-seen cutoff. For non-empty master input, `main` prunes scores against the selected job list; because `--since` filtering happens first, it can also prune scores for older jobs still in the master. `--dry-run` returns before pruning or model calls. Each verdict is saved incrementally into compact `scores.json` with JD coverage and scoring time; errors are stored for retry, but the script still returns success after a batch containing model errors. Evidence: `triage_agent.py::main`.

JD handling is source-specific: Indeed uses the current source snapshot's description cache, LinkedIn re-fetches the guest posting endpoint, and a small ATS allowlist fetches page text. It does not generally reuse `job.description` from the master. Other boards are metadata-only. Evidence: `fetch_jd`, `_indeed_jds`, `JD_FETCHABLE_ATS`, `_extract_text`.

The API backend requires the Anthropic SDK and key, defaults to `claude-haiku-4-5-20251001`, and sends a cached static profile/resume prefix plus one job prompt. Otherwise it runs logged-in `claude -p --tools ""` with a 120-second timeout; the CLI call does not pass `--model`. Parsing extracts a JSON object, clamps/coerces score, and defaults invalid verdict labels to `maybe`; it does not enforce the other required prompt fields or role-family vocabulary. Heuristic redaction removes detected private tokens from published rationale/seniority/opener/flags. It is not proof of complete private-data removal. Evidence: `make_call_model`, `parse_verdict`, `private_tokens`, `redact_private`.

**CURRENTLY DISABLED:** `triage.yml` has no nightly schedule despite its display name, and `evals.yml` has neither schedule nor push trigger. Both are manual-only. The eval step skips when the profile secret is empty. Evidence: the two workflow trigger blocks and eval step condition.

`eval_triage.py` contains 10 synthetic cases and uses the same prompt/backend/parser/redaction path without writing scores. The cases retain health/biomedical ML expectations; some require `ml-ai`, `biotech-informatics`, or `security`, while `triage_agent.py::ROLE_FAMILIES` prompts an environmental/toxicology vocabulary lacking those tokens. Neither vocabulary is derived from the current personal role categories. Evals were not run in this audit; model quality and compatibility with any remote candidate profile are **UNKNOWN / NEEDS VERIFICATION**. Evidence: `eval_triage.py::CASES`, `run_case`, `check`; `triage_agent.py::ROLE_FAMILIES`.

## GitHub Actions and scheduling

All 21 files under `.github/workflows/` were read. The following are literal UTC cron definitions; they do not adjust for UK/Pacific daylight saving. Remote enablement and actual scheduler execution remain **UNKNOWN / NEEDS VERIFICATION**.

| Workflow file | Current trigger / gate |
|---|---|
| `linkedin_watch.yml` | CURRENT scheduled `17 15-23,0-3 * * *`; manual optional 30-day backfill |
| `indeed_watch.yml` | CURRENT scheduled `47 15-23,0-3 * * *`; manual optional 50-day backfill |
| `glassdoor_watch.yml` | Scheduled `07 16-23,0-3 * * *`; job gated by opt-in variable or manual dispatch |
| `ziprecruiter_watch.yml` | Scheduled `27 16-23,0-3 * * *`; local discovery lists empty |
| `google_jobs_watch.yml` | CURRENT scheduled `37 16-23,0-3 * * *`; manual backfill flag |
| `hiringcafe_watch.yml` | Scheduled `57 16-23,0-3 * * *`; local discovery list empty; manual 61-day backfill |
| `linkedin_watch_backup.yml` | CURRENT watchdog `33 15-23,0-3 * * *`, plus manual dispatch |
| `weekly_digest.yml` | CURRENT scheduled `30 16 * * 1`, plus manual days/force inputs; sending is opt-in |
| `sync_upstream.yml` | CURRENT scheduled `0 6 * * 1`, plus manual dispatch |
| `scrape_jobs.yml` | LEGACY BUT STILL PRESENT priority digest; automatic scheduling CURRENTLY DISABLED; manual backfill input |
| `usajobs_watch.yml` | LEGACY BUT STILL PRESENT; manual-only |
| `calcareers_watch.yml` | LEGACY BUT STILL PRESENT; manual-only |
| `csucareers_watch.yml` | LEGACY BUT STILL PRESENT; manual-only |
| `localgov_watch.yml` | LEGACY BUT STILL PRESENT; manual NEOGOV/CalOpps, optional NEOGOV 60-day backfill |
| `triage.yml` | LEGACY BUT STILL PRESENT; manual-only scoring |
| `evals.yml` | LEGACY BUT STILL PRESENT; manual-only model evals, profile-gated step |
| `linkedin_backfill.yml` | Manual two-phase matrix/artifact backfill |
| `clear_data.yml` | Manual data reset; always commits regardless of `ENABLE_DATA_COMMITS` |
| `notify_test.yml` | Manual Pushover delivery test |
| `validate_setup.yml` | Manual local-file/variable/secret-presence checks |
| `tests.yml` | Push/PR path-filtered tests, plus manual dispatch |

Watcher/data-writer workflows use Python 3.11 on Ubuntu and the `job-scraper-commit-push` concurrency group with `cancel-in-progress: false`; parallel-backfill merge jobs share that group. This covers the entire relevant workflow/job, not just its final push step. The watchdog, weekly digest, evals, tests, validation, notification test, and upstream sync do not share that group. Evidence: workflow concurrency blocks.

Normal collector/triage commits use force-add for ignored output, commit only if staged data changed, then pull with `--rebase -X ours` from `origin main` and push. The commit flag does not gate scraping, notification attempts, or workflow logging. Workflows naming `output/notified.json` in `git add` can fail when that file is absent, because notification code does not create it without credentials; it exists in this checkout. Evidence: watcher/triage commit steps, `notify_new_jobs`.

The watchdog checks latest run creation hour/status for LinkedIn and Indeed, dispatching `main` if no run exists that UTC hour and none is queued/in-progress. It does not check run conclusion or retry a failed same-hour run. Its Indeed step waits 90 seconds before inspection; this precedes Indeed's native :47 slot, so a rescue and later native trigger are both possible. Evidence: `linkedin_watch_backup.yml` commands. External trigger services are not configured in the inspected repository.

Parallel backfill writes `config.json` from `CONFIG_JSON` secret in each job, unlike normal watchers. Missing/empty secret therefore produces an invalid personal JSON file and example fallback. Despite comments about fallback to a single run when partitions are empty, the actual matrix emitter always adds US-wide and Remote low-volume locations; with the local 11 terms this would create 12 low-phase work items, while the empty high-volume list yields zero high-phase items. Worker day slicing uses the 30-day constant, despite seven-day comments. Evidence: `linkedin_backfill.yml`, `scrape_jobs.py` `--linkedin-emit-matrix` and partition branches.

Backfill merges download matching artifacts, reset to latest `origin/main`, merge artifact JSON, save output, and delete term/partition files. They force-add `output/deltas/`, but the inspected code produces no such directory and none exists locally; commit steps can fail on that path. The hard reset also makes the effective merge-job configuration depend on which configuration is tracked on remote `main`, rather than guaranteeing the earlier secret-written contents survive. Evidence: backfill merge steps, `_linkedin_merge_backfill_files`, `--linkedin-merge-backfill`, tree inspection. No backfill workflow was dispatched.

`sync_upstream.yml` fetches `ScottCoffin/Job_Scraper` main, merges with `-X ours`, backs up/restores personal configuration files, and pushes without the data-commit gate or shared writer concurrency group. `.gitattributes` declares `merge=ours` for personal configuration and `merge=union` for workflow-run logs; no custom `merge.ours.driver` is configured in this local checkout or set by the inspected workflow. Attribute declarations alone do not establish a functioning custom driver remotely.

`clear_data.yml` resets its explicit source JSON list, master, and notification tracker. It omits CSU JSON, scores, Markdown/HTML digests, workflow logs, and browser state. `validate_setup.yml` checks config existence and data-commit variable as required items; it does not parse configuration, verify Pages deployment, prove collector health, or verify delivery. `scripts/setup.sh` requests Actions/Pages settings and optionally dispatches LinkedIn/Indeed/ZipRecruiter/HiringCafe backfills; it does not set up AI scoring or commit the personal config. Evidence: these files' commands.

## Schema inconsistencies — CURRENT

`schema/jobs.schema.json` is a Draft 2020-12 single-object schema requiring non-empty HTTP(S) URL, title, company, a permitted `ats`, and timestamp-shaped `first_seen`. Additional properties are allowed. It has no envelope schema, retention constraint, uniqueness constraint, or complete model-verdict schema. The scraper/notifier/agent/dashboard do not invoke this schema at runtime. Evidence: schema and the inspected producer/consumer code.

Read-only validation of every local JSON `jobs` record with `jsonschema.Draft202012Validator` found:

- Master: **24 of 438 invalid**, all because `is_remote=null` conflicts with the schema's boolean-only property. `_coerce_bool`, `_ingest_jobspy_df`, and Google normalizers can emit `None` rather than omit the property.
- All **66 jobs in non-empty source snapshots** lack required `first_seen`. Four Google source records additionally contain null `is_remote`. `save_jobs_output` writes original source records, while `_merge_into_all_jobs` stamps copies, explaining that difference.
- Empty snapshots cannot establish record-schema compatibility. `notified.json` is not a job envelope and was not treated as one.

The schema's description says descriptions are absent for government-board sources, but `_parse_csucareers_listing` produces a summary description. It does not describe `closing_date`, though permissive additional properties allow it. The AI JD allowlist/dashboard recognize Phenom/Lever/Ashby beyond the schema's `ats` enum; the current curated producer is empty and no such labels were observed in the local master. Evidence: schema descriptions/enum, `_parse_csucareers_listing`, `JD_FETCHABLE_ATS`, `classifySource`.

## Test status — CURRENT observed result

The default system Python and bundled Python initially failed to start pytest because pytest was absent. Existing `tests/requirements-dev.txt` dependencies were installed into `/private/tmp/job-scraper-audit-venv`, outside the repository. The existing suite was then run with cache generation disabled:

```text
/private/tmp/job-scraper-audit-venv/bin/python -m pytest tests/ -v --ignore=tests/local -p no:cacheprovider
Python 3.14.0; pytest 9.1.1; jsonschema 4.26.0
187 collected; 185 passed; 2 failed; 0.80 seconds; exit code 1
```

Failures were `tests/test_master_jobs_file_merge.py::test_preserves_existing_fields_on_duplicate` and `::test_preserves_false_tag_on_duplicate`, both raising `StopIteration` when looking for a retained fixture job. `tests/fixtures/sample_all_jobs.json` has fixed August 10–14 `first_seen` timestamps. On September 15 those records are outside the merge's 30-day window; merge output reported zero retained jobs in these two cases. This explains the observed failure before the field assertions can run. No tests or code were changed, and the clock was not overridden.

Tests cover dedupe helpers, master merging, LinkedIn card/JD parsing, mixed partition-file merging, slug generation, configured location filtering, work modes, fixture schema compatibility, neutral defaults, workflow text boundaries, and personal search configuration. `tests/conftest.py` redirects scraper output to temporary directories. They do not demonstrate live board availability, remote Actions execution, actual Pushover delivery, browser interaction correctness, or model quality. The schema test validates the synthetic master fixture, not real output. Python 3.11 CI execution remains **UNKNOWN / NEEDS VERIFICATION**, because this local run used 3.14.

`tests.yml` installs only test requirements and runs `pytest tests/ -v --ignore=tests/local`. Its push paths include scraper, tests, and the test workflow; PR paths include scraper and tests. Changes only to notifier, dashboard, schema, config, AI scripts, or other workflows do not directly match those test triggers. Root `test.py` is an unrelated requests/BeautifulSoup coordinate-grid decoder and is outside the configured suite. Model evals are separate and were not executed. Evidence: `tests.yml`, `tests/requirements-dev.txt`, `tests/*.py`, `test.py`, `eval_triage.py`.

## Known technical debt — CURRENT factual findings

- Personal configuration is untracked locally, while documentation calls it tracked; the remote configured search cannot be inferred from this checkout. Old generated scope remains visible. Evidence: Git inspection, `config.json`, `README.md`, output artifacts.
- Configuration semantics diverge among scraper, dashboard, notifier, and AI inputs; unused metadata and `notify.min_fit` do not drive runtime behaviour. Evidence: the configuration section above and named loaders.
- Query disablement and zero-row snapshot preservation are conflated for some collectors; workflow timestamps can advance while stale data is reused. Evidence: `_scrape_jobspy_board`, `scrape_hiringcafe_recent`, `save_jobs_output`.
- Schema-required discovery timestamps and boolean-only remote flags do not match all producer outputs; runtime validation is absent. Evidence: schema validation findings and producer functions.
- Generic URL identity can collapse distinct query-identified jobs, and content matching retains US-centric stopwords. Pairwise heuristic matching/clustering can become costly as job count grows. Evidence: `_job_identity`, `_same_job`, `_dedupe_master_jobs`, dashboard `dedupe`.
- Master persistence fills sparse fields but keeps non-empty old content; direct writes lack atomic replacement and transaction coordination. Broad failure guards can leave source output ahead of master data. Evidence: `_merge_duplicate_job`, `_merge_into_all_jobs`, `save_jobs_output`.
- Notifier priority-topic configuration is disconnected, delivery failures still consume identities, and browser/notifier scoring differs. Evidence: `notify.py::STAR_TERMS`, `notify_new_jobs`, both fit functions.
- Dollar-oriented salary parsing and US/Australian geocoding do not establish correct pay/map interpretation for the configured UK/China scope. Evidence: `format_salary`, dashboard salary/map functions.
- AI prompt families, eval families, and personal dashboard buckets diverge; stored scores use raw URLs, and `--since` can narrow score-pruning membership. Evidence: AI/eval sections and `triage_agent.py::main`.
- Parallel-backfill comments and commands disagree on empty partitions/day windows; absent `output/deltas/` is still staged. Reset coverage omits some current data files. Evidence: `linkedin_backfill.yml`, emitter branches, `clear_data.yml`.
- Fixed-date fixtures make two field-preservation tests fail at the present date; test triggers and fixture validation leave substantial paths unverified. Evidence: test result, fixture timestamps, `tests.yml`.

These are observations of existing behaviour, not fixes or implementation proposals.

## Current compatibility contracts

The operational contracts consumers currently rely on are the existing output filenames/envelopes, `jobs` arrays, raw `url` values, `ats` source labels, and source-varying date/salary/description fields. `first_seen` belongs to master insertion and retention; source envelopes normally include newness counts/lists, with the legacy three-key exception. `updated_at`/`scraped_at` use display strings `YYYY-MM-DD HH:MM UTC`, while master discovery timestamps use UTC ISO strings. Evidence: `save_jobs_output`, `save_results`, `_merge_into_all_jobs`, `triage.html::loadJobs`, `triage_agent.py::load_jobs`.

Master merge preservation applies to arbitrary fields already on surviving records, including true/false downstream tags; it is not permanent archival retention or a general merge of incoming consumer fields. Alternate posting URLs are accumulated in `duplicate_urls`; schema permits extensions but does not validate all extensions. Evidence: `_merge_duplicate_job`, `_merge_into_all_jobs`, schema and merge tests.

AI scores remain a separate URL-keyed map with optional fields and `error` retry semantics. The dashboard's local decisions remain URL-keyed browser state under the v3 storage key, with no migration from older additive cache keys. A change in the primary duplicate URL can therefore affect which annotations or scores are displayed. Evidence: `triage_agent.py::main`, dashboard state initialization, `enrich`, `_mergeCluster`.

Workflow/script invocation contracts include the current source-only/backfill flags, boolean backfill workflow inputs, personal/example JSON configuration names, environment-based credentials, literal `main` references, and `ENABLE_DATA_COMMITS` as a repository variable controlling output commits. Google exact queries support both strings and objects with `query/location/country`, preserving the string-only input path. Evidence: `scrape_jobs.py::__main__`, `_google_jobs_query_contexts`, workflow files, notification/AI environment readers.

## Important uncertainties — UNKNOWN / NEEDS VERIFICATION

- Remote branch contents, tracked personal configuration, repository variables/secrets, Actions enablement/permissions, Pages settings/custom domain, and whether the working-tree workflow edits are deployed.
- Actual collector reachability, blocking, completeness, geographic interpretation of LinkedIn Remote/HiringCafe queries, and whether provider-specific recency/locale behaviour matches requests.
- Why local generated output stops at September 5, whether zero-data preservation occurred, and which configuration produced each historical artifact.
- Live notification delivery, remote weekly/Glassdoor opt-in state, external dispatch services, and remote merge-driver configuration.
- End-to-end parallel-backfill behaviour, especially empty matrices, artifact/reset interactions, missing delta paths, and actual capped-query coverage.
- AI performance/privacy outcomes for the remote profile/model/backend, browser runtime behaviour and localStorage quota handling, and CI Python 3.11 results.

The supporting local evidence is named in the preceding sections. No remote workflows, notifications, setup changes, or model calls were triggered to resolve these uncertainties.

## Inspection record

Read source/configuration: `config.json`, `config.example.json`, `scrape_jobs.py`, `notify.py`, `triage_agent.py`, `eval_triage.py`, `triage.html`, `schema/jobs.schema.json`, `scoring_profile.example.json`, `requirements.txt`, `.gitignore`, `.gitattributes`, `scripts/setup.sh`, `scripts/export-config-secret.sh`, and root `test.py`. `README.md`, `CLAUDE.md`, and `docs/AGENT_README.md` were consulted as secondary prose; behavioural claims above are grounded in code/data rather than accepted from that prose.

Read all workflow files listed in the scheduling table. Read all 13 test modules under `tests/` (`test_job_deduplication.py`, `test_linkedin_jd_extraction.py`, `test_linkedin_partition_merge.py`, `test_linkedin_partition_merge_mixed.py`, `test_linkedin_search_result_parsing.py`, `test_location_filter_us_states.py`, `test_master_jobs_file_merge.py`, `test_partition_key_slugify.py`, `test_phase1_neutral_defaults.py`, `test_phase1_workflow_defaults.py`, `test_phase2_personal_config.py`, `test_schema_validation.py`, `test_work_arrangement_classification.py`), shared `conftest.py`, the empty test initializer, and test requirements; inspected fixture structure/content used by these tests.

Inspected every local output JSON file listed in the data table plus `notified.json`, parsed its job records for shape/schema observations, sampled `workflow_runs.jsonl`, and read representative `jobs.md/.html`, `google_jobs.md/.html`, and `governmentjobs_jobs.md`. Inspected the repository tree and Git state before document creation. This audit creates only `docs/references/current-repository-audit.md`; existing source/configuration/workflow/test/output contents were left unchanged.
