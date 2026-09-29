# Canonical Job Foundation

Status: Active
Classification: PLAN
Last updated: 2026-09-16

Starting revision: `e266dca245b4c355758637f5b9f81db7ca4dc06b`, qualified
by a local working tree that already contains the Accepted canonical Job design
and its catalog/handoff edits. Preserve unrelated changes and re-check `git status`
before every milestone. This plan is the implementation record; it must be updated
as work proceeds rather than treated as a static checklist.

## Purpose / Big Picture

Implement the first bounded foundation described by the
[Accepted canonical Job design](../../design-docs/canonical-job-model.md), while the
existing JSON pipeline remains authoritative. The observable result is an executable
Python domain contract for a Canonical Job and its source observations, explicit
legacy-to-canonical and canonical-to-legacy adapters, and a controlled Indeed path
that crosses those boundaries before continuing through the existing persistence
and consumer flow.

At completion:

- Canonical facts, source/provenance evidence, observation metadata, scoped
  identities and identity outcomes have executable representations and validation.
- Current normalized job dictionaries can enter the domain without turning missing
  values into false facts, and can project back to existing-compatible dictionaries.
- Indeed records pass through the canonical boundary and compatibility projection
  before `save_jobs_output`; source snapshots, master JSON, digests and notification
  inputs retain their current externally visible forms.
- `_merge_into_all_jobs` continues to own current JSON accumulation/retention and
  receives compatibility records; it is not replaced by a new store or silently
  reclassified as canonical identity resolution.
- Contract tests enforce the accepted invariants, including provenance, URL/time
  distinctions and conservative identity outcomes.

This milestone does not deliver Postgres, universal collector migration, complete
cross-source canonicalization, direct-URL resolution, live verification, or
application intelligence.

## Context and Orientation

### Current pipeline and representation

[scrape_jobs.py](../../../scrape_jobs.py) is a root-level module, not part of an
installed Python package. Its import-time `_load_config` deep-merges
`config.json` over `config.example.json`. Collectors produce mutable dictionaries.
The common writer `save_jobs_output` filters employers, mutates records with
`_ensure_work_arrangement`, computes source newness from `_job_identity(url)`, calls
`_merge_into_all_jobs` with the full current source window, calls
`notify.notify_new_jobs` with source-new dictionaries, and writes source
JSON/Markdown/HTML. `save_results` remains a legacy three-key-envelope exception.

JobSpy sources share `_ingest_jobspy_df`. It creates dictionaries containing
`company`, `title`, `location`, `url`, `direct_url`, `date_posted`, truncated
`description`, formatted `salary`, `salary_source`, `salary_currency`, `job_type`,
nullable `is_remote`, derived `work_arrangement`, `emails`, `company_url`, and a
mixed-source `ats` label. `scrape_indeed_recent` invokes this shared normalizer with
`label="Indeed"`; `save_indeed_results` delegates to `save_jobs_output`. A zero-row
JobSpy run can reuse the previous source snapshot, so a saver invocation is not
proof of a new upstream observation. Do not fabricate `observed_at` in that case.

### Identity and persistence

`_job_identity` recognizes selected source/ATS URL IDs and otherwise normalizes
host/path. `_same_job` first compares those identities, then uses company/title and
location or description similarity. `_dedupe_master_jobs` and
`_merge_into_all_jobs` use that legacy behavior; `_merge_duplicate_job` fills only
selected missing fields and accumulates `duplicate_urls`. These are CURRENT
compatibility behaviors. They are not the Accepted design's canonical
`AUTO_MERGE / POSSIBLE_MATCH (review) / KEEP_SEPARATE` contract.

`_merge_into_all_jobs` stamps newly inserted master copies with `first_seen`, never
updates a `last_seen`, prunes lexically at 30 days, and writes compact
`output/all_jobs.json` as `{updated_at,jobs}`. Existing master records retain
arbitrary downstream fields. `save_jobs_output` writes source snapshots as
`{scraped_at,total,new_count,jobs,new_jobs}`. `save_results` writes
`{scraped_at,total,jobs}`. The current
[single-record JSON schema](../../../schema/jobs.schema.json) requires `url`,
`title`, `company`, mixed-label `ats`, and `first_seen`; it does not describe an
envelope or the target domain model.

### Consumers and tests

- [triage.html](../../../triage.html), `SOURCES` and `loadJobs`, fetches fixed source
  files plus the master, unions exact raw `url` values, backfills missing source
  `first_seen` from the master, then derives classifications and clusters records.
  `jobTriage:v3`, notes, stars and workflow decisions remain raw-URL keyed.
- [notify.py](../../../notify.py), `_identity`, keys instant-notification history by
  normalized company/title. Weekly selection reads master `first_seen`; optional
  agent scores are looked up by raw `url`.
- [triage_agent.py](../../../triage_agent.py), `load_jobs` and `main`, reads master
  dictionaries by default and persists raw-URL-keyed `scores.json` entries.
- [tests/conftest.py](../../../tests/conftest.py) places the repository root on
  `sys.path` and redirects `scrape_jobs.OUTPUT_DIR` to a temporary directory.
  `test_job_deduplication.py` covers legacy matching; `test_master_jobs_file_merge.py`
  covers master persistence and field preservation; `test_schema_validation.py`
  validates a fixture against the legacy schema; and
  `test_work_arrangement_classification.py` covers current heuristic labels.
  There is no automated browser suite or notification contract suite.

Read-only inspection on 2026-09-16 found the current local master envelope with 438
jobs and the Indeed source envelope with six jobs. The union of observed master
keys includes all JobSpy fields plus `first_seen` and `duplicate_urls`. These are
local examples, not exhaustive or remote-runtime claims.

### Planned file boundary

Use two root-level standard-library modules rather than introducing a `src/`
hierarchy:

- `canonical_job.py`: domain value types, validation, opaque canonical identity
  interface, scoped source/ATS identities, source observations, Canonical Job, and
  identity evidence outcome types.
- `job_compat.py`: transformations between legacy dictionaries and composed
  canonical records, plus compatibility projection.

This is a task-local implementation decision. Both modules have immediate consumers
and are importable using the repository's established test setup. A package tree,
processing layer and storage layer would add packaging/refactor work without a
second concrete implementation boundary in this milestone. Revisit packaging only
when later work supplies that need.

Use `dataclasses`, `enum`, `datetime`, immutable tuples and read-only/copy-on-write
mappings from the standard library. Do not add dependencies. The Python contract
and its tests are the first executable authority; the existing JSON schema remains
a legacy compatibility declaration. Do not label that schema canonical or create
a second hand-maintained schema that could drift from the Python contract.

## Scope and Non-goals

### In scope

1. `canonical_job.py` with minimally sufficient representations for Canonical Job,
   source observations, scoped identities, observed links/compensation/deadlines,
   accepted time semantics, optional/unknown values, and identity outcomes.
2. `job_compat.py` with explicit legacy input context, transformation and legacy
   projection. Compatibility-only extensions must be retained outside factual core
   fields and round-trip without silently becoming canonical facts.
3. A conservative identity evaluation boundary. It may return `AUTO_MERGE` only for
   a matching scoped source identity or matching scoped ATS identity with no
   material contradiction. Ambiguous composite evidence returns
   `POSSIBLE_MATCH`; insufficient/contradictory evidence returns `KEEP_SEPARATE`.
4. Unit, contract and no-network integration tests for accepted semantic rules and
   current compatibility behavior.
5. The Indeed save path as the pilot, followed by the existing source/master/
   notification boundaries using compatibility dictionaries.
6. An explicit master-persistence integration contract: current JSON merge remains
   legacy behavior and storage authority, consuming projected records.

### Non-goals

- PostgreSQL/Supabase, migrations, shadow writes, parity or cutover.
- Notion ownership or synchronization.
- Live ATS verification or `LIVE / CLOSED / UNKNOWN` implementation.
- Broad direct-application URL discovery or reliability scoring.
- Phase 2 role taxonomy, eligibility, Fit Score, Daily Priority, shortlist, skills,
  interview preparation or candidate workflow.
- A Company entity, legal-entity resolution or company alias service.
- Provider-ranking tables, currency conversion or complete compensation modeling.
- Numeric fuzzy matching thresholds or replacement of legacy `_same_job` behavior.
- Migration of every collector, `save_results`, dashboard JavaScript identity,
  notifications, or legacy AI storage to canonical identifiers.
- A full `scrape_jobs.py` rewrite, new package hierarchy, service framework or
  cosmetic repository-wide refactor.

## Compatibility Constraints

Internal TARGET semantics and external legacy semantics must stay explicit:

| Boundary | Internal canonical rule | External compatibility rule during this plan |
|---|---|---|
| Job identity | Opaque canonical ID plus scoped source/ATS evidence; URL is not canonical identity. | Preserve raw `url`, current `_job_identity`, `_same_job`, `duplicate_urls`, source-newness behavior and master merge outcome. Do not expose a canonical ID under a current key. |
| Source/ATS | Collection source and ATS provider/ID are distinct. | Preserve current mixed `ats` source label exactly; do not overwrite it with canonical ATS provider. |
| Application links | `source_url` and application-link roles are distinct; preferred link is a non-identifying projection. | Preserve current `url` and `direct_url`, including equal values and empty strings. Raw URL keys for dashboard/scores do not change. |
| Observation time | `first_seen_at`/`last_seen_at` are accepted observation metadata and obey ordering; missing remains unknown. | Preserve legacy `first_seen` text and 30-day retention meaning. Do not rename or synthesize `last_seen` in JSON. Source snapshots continue to omit `first_seen` when they do today. |
| Posting/deadline | Posting time differs from observation time; deadline observations retain provenance/conflicts. | Preserve `date_posted`, CSU `closing_date`, empty strings and extra fields. Do not add urgency or select provider precedence. |
| Unknown values | `None`/absence remains unknown unless evidence is explicit. | Projection must reproduce omission versus present `null` versus `false` versus empty string for compatibility fields. In particular, do not make nullable `is_remote` false. |
| Work arrangement | Explicit wording belongs to provenance; normalized work arrangement is derived and cannot affect identity. | Preserve current `work_arrangement`, `telework`, `job_type` and `is_remote` values. `_ensure_work_arrangement` remains the legacy output heuristic. |
| Compensation | Source observations remain provenance; canonical preferred view is traceable; calculated comparison values are derived. | Preserve `salary`, `salary_source`, `salary_currency` and current strings. No conversion, annualization or zero default. |
| Candidate/workflow | Never part of factual core or identity. | Existing arbitrary master extensions, URL-keyed browser annotations and URL-keyed agent scores survive unchanged. Adapter extras round-trip without promoting them into identity. |
| Envelopes/files | Domain objects are internal. | Keep `output/all_jobs.json`, every source filename, envelope keys, pretty/compact formatting choices, Markdown/HTML digests, CLI flags and workflow commands/paths. |
| Notifications | Canonical identity does not replace delivery identity in this milestone. | `notify_new_jobs` receives projected dictionaries; `_identity` output and `notified.json` behavior remain unchanged. |

No change may be justified solely because the legacy schema calls `url` a primary
key or calls its mixed source label `ats`. Tests must preserve those external
aliases while separately testing target semantics.

## Progress

- [ ] 2026-09-16 — Milestone 1: establish executable domain contract.
- [ ] 2026-09-16 — Milestone 2: encode domain validation and contract tests.
- [ ] 2026-09-16 — Milestone 3: add legacy-record-to-canonical transformation.
- [ ] 2026-09-16 — Milestone 4: add canonical-to-legacy compatibility projection.
- [ ] 2026-09-16 — Milestone 5: integrate and validate the Indeed pilot path.
- [ ] 2026-09-16 — Milestone 6: validate the master persistence boundary.
- [ ] 2026-09-16 — Milestone 7: classify and safely bound remaining producers.
- [ ] 2026-09-16 — Milestone 8: complete compatibility/regression validation and
  close or hand off the plan.

No implementation milestone is complete at plan creation. Next executable action:
write the failing domain contract tests described in Milestones 1–2, then implement
only enough `canonical_job.py` to satisfy them.

## Surprises & Discoveries

- 2026-09-16 — CURRENT `ats` is a collection/source label for LinkedIn, Indeed,
  GoogleJobs and HiringCafe as well as an ATS-like label for Greenhouse/Workday.
  Effect: adapter input requires an explicit source context and cannot infer a
  canonical ATS provider from every legacy `ats` value.
- 2026-09-16 — Source records and master records have different timestamp shapes:
  `save_jobs_output` writes original source jobs, while `_merge_into_all_jobs`
  stamps new master copies with `first_seen`. Effect: legacy `first_seen` maps only
  as known observation evidence; its absence remains unknown.
- 2026-09-16 — JobSpy zero-row preservation can pass cached records through a fresh
  saver invocation. Effect: `save_indeed_results` cannot honestly assign a new
  `observed_at`; the pilot adapter must accept an absent observation time unless
  the collector supplies evidence.
- 2026-09-16 — Identity is consumer-specific: scraper/master matching, dashboard
  clustering, notification company/title identity, and raw-URL score/state keys
  differ. Effect: canonical identity is additive and internal in this plan; no
  consumer key is replaced.
- 2026-09-16 — `_coerce_bool` and JobSpy/Google records can persist `is_remote=None`
  while the legacy schema allows only boolean. Effect: the domain preserves unknown
  and compatibility tests cover null; this plan does not conceal drift by coercion.
- 2026-09-16 — `schema/jobs.schema.json` describes one record, not source/master
  envelopes, and runtime writers do not invoke it. Effect: it remains a legacy
  fixture contract; Python domain validation becomes the executable canonical
  contract for this milestone.
- 2026-09-16 — Dashboard state and legacy AI scores depend on raw URLs. Effect:
  round-trip tests must prove URLs are byte-for-byte stable and notification/score
  lookup behavior is unchanged for projected records.

Add dated entries here when implementation evidence changes sequencing or exposes
a constraint. A conflict with Accepted semantics is a stop condition: record the
evidence and request design review rather than changing the design inside this plan.

## Decision Log

- 2026-09-16 — Use root modules `canonical_job.py` and `job_compat.py`. Rationale:
  the repository already imports root modules directly; domain and compatibility
  each have an immediate consumer; a `src/job_search/...` package would add
  packaging and broad import work without improving this bounded pilot.
- 2026-09-16 — Use standard-library dataclasses/enums and explicit validation; add
  no dependency and do not create a second JSON schema. Rationale: one executable
  Python authority avoids manual schema duplication while existing JSON remains a
  compatibility format.
- 2026-09-16 — Pilot `save_indeed_results`, not a live scrape. Rationale: its records
  are representative (salary/currency, nullable remote, derived work mode,
  source/direct URLs and stable `jk` IDs), the saver reaches master and notification
  boundaries, and synthetic inputs exercise it without provider/network behavior.
- 2026-09-16 — Keep legacy `_same_job` and `_merge_into_all_jobs` decisions as
  compatibility behavior. Rationale: replacing them would solve the broader
  cross-source identity problem and risk changing current JSON; the new identity
  interface is tested independently and initially conservative.
- 2026-09-16 — Preserve ambiguous legacy records in a composed adapter result:
  canonical facts/observations plus compatibility extras. Rationale: lossless
  projection is necessary without claiming every legacy extension is canonical.

Record later task-local choices here with date, evidence and consequence. Durable
semantic changes belong in the Accepted design and require explicit review.

## Plan of Work

### Milestone 1 — Establish executable domain contract

Create `canonical_job.py`. Define minimal frozen value objects for an opaque
`CanonicalJobId`, namespaced `ScopedIdentity`, observed links, compensation and
deadline values, `SourceObservation`, and `CanonicalJob`. Keep explicit source
wording/evidence on observations; keep normalized work arrangement and role family
outside factual identity. Represent unknown optional values as `None` and keep
absence distinguishable in the compatibility adapter rather than inventing a
universal null enum.

Define an `IdentityOutcome` enum with `AUTO_MERGE`, `POSSIBLE_MATCH` and
`KEEP_SEPARATE`, plus an evidence/result object. The initial evaluator handles only
safe deterministic scoped-identity equality and explicit contradictions. Composite
signals may produce `POSSIBLE_MATCH`; fuzzy title similarity alone must never
produce `AUTO_MERGE`. Do not copy current Jaccard thresholds.

Validation rejects internally contradictory times (`first_seen_at > last_seen_at`),
unscoped IDs, and an asserted preferred value/link with no supporting observation.
It must not reject unknown optional values merely because legacy schema does.

### Milestone 2 — Encode core domain validation and contract tests

Create `tests/test_canonical_job_domain.py` first. Unit tests cover value-object
construction, UTC/time ordering, unknown preservation, scoped source versus ATS
identity, link roles, compensation/deadline evidence, and exclusion of candidate/
workflow/derived fields from identity inputs. Identity contract tests cover:

- same scoped source posting with no contradiction → `AUTO_MERGE`;
- same scoped ATS provider + tenant/employer namespace + opening ID with no
  contradiction → `AUTO_MERGE`;
- similar title alone → never `AUTO_MERGE`;
- composite agreement without shared deterministic identity → `POSSIBLE_MATCH`;
- conflicting scoped ATS/requisition IDs, incompatible employer, materially
  incompatible location-specific evidence, materially different requisition
  content, or explicit simultaneous-opening evidence → `KEEP_SEPARATE` and block
  `AUTO_MERGE`.

Tests must use named evidence rather than numeric similarity cutoffs. Deadline tests
assert nullable/unknown, multiple source observations, visible conflict, traceable
preferred projection and no urgency field. Work-arrangement tests assert explicit
source wording remains in provenance while a separate derived value can reference
the Job without influencing identity.

### Milestone 3 — Add legacy-record-to-canonical transformation

Create `job_compat.py` and `tests/test_canonical_job_compat.py`. Define an adapter
input context containing source label and optional actual observation time; neither
is guessed from save time. Transform current dictionaries into a composed result
containing Canonical Job, one or more SourceObservations, and a defensive copy of
compatibility-only fields.

Map title/company/location/description as observed source facts and candidate
preferred factual views only when present. Normalize employer text with a minimal,
documented whitespace/case policy; preserve source spelling. Treat `salary`,
`salary_currency` and `salary_source` as compensation evidence; any preferred view
must reference that evidence. Map `date_posted` without claiming precision beyond
the string that can be parsed safely. Map `closing_date` or a legacy
`application_deadline` as observed deadlines, preserving the original field/value.

Map `url` as source/link evidence and `direct_url` as a distinct application-link
role even when equal. Preserve mixed `ats` as source-label evidence; populate ATS
provider/ID only from independently recognized scoped evidence, never just by
renaming the legacy label. Preserve `is_remote`, `work_arrangement`, `telework` and
`job_type` as original/derived compatibility evidence; `None` stays unknown.

Map legacy `first_seen` to known canonical observation metadata only when it parses;
do not infer `last_seen_at`, overwrite the original string, or use posting date as
discovery time. Invalid/ambiguous values remain compatibility evidence and unknown
canonical time. Exclude bookmarked/notes/status/scores and other candidate/workflow
extensions from facts and identity while retaining them for projection.

The adapter receives or is assigned an opaque provisional canonical ID. For a
single ungrouped legacy record, use a documented compatibility namespace derived
from a scoped source posting identity when safely available; otherwise inject an
ID from the caller. The value is internal and must not be exported as legacy `url`
or asserted as a complete cross-source merge solution.

### Milestone 4 — Add canonical-to-legacy compatibility projection

Implement projection in `job_compat.py`, with golden fixtures under
`tests/fixtures/` only where exact dictionary equality is clearer than inline data.
Projection starts from the preserved compatibility record and deliberately overlays
only mapped legacy fields. It preserves key presence, empty string versus null versus
false, raw URL values, mixed `ats`, original `first_seen`, source date/deadline
aliases, `duplicate_urls`, and arbitrary downstream extensions.

Add round-trip contract tests for a representative Indeed record, a sparse source
record, a master record with `first_seen` and false/user fields, a CSU-like
`closing_date`, equal/different source/application URLs, and unknown remote/salary/
deadline values. Verify projection does not add canonical-only IDs, source
observation metadata, role classification or candidate analysis to current JSON.
Keep `schema/jobs.schema.json` unchanged unless implementation uncovers a genuine
legacy contract error; record such a discovery before proposing a separate change.

### Milestone 5 — Integrate one controlled current path

Modify only `save_indeed_results` and a small named helper in `scrape_jobs.py` to
perform:

```text
current Indeed dictionary
        → legacy adapter/context
        → Canonical Job + provenance
        → compatibility projection
        → existing save_jobs_output
```

Pass no fabricated observation time from the saver. Preserve list order and make
no network call. `save_jobs_output` must receive projected dictionaries equal to
the input for compatibility-relevant fields, then perform its existing exclusion,
work-arrangement, source-newness, master, notification and output behavior.

Create `tests/test_canonical_job_integration.py`. Patch notification delivery and
use `tmp_output_dir`; feed a synthetic Indeed dictionary through
`save_indeed_results`. Compare the resulting source envelope/records, master
record fields, `_job_identity`, notifier `_identity`, and raw score lookup key with
the pre-integration expectations. Pin time where timestamps matter. Do not invoke
JobSpy or any live service.

The pilot is representative because Indeed/JobSpy emits the richest common current
shape and a stable query ID, while the saver is provider-thin and shared downstream.
It is lower risk than LinkedIn enrichment, Google fallback/provider selection,
HiringCafe SSR parsing, or legacy government collectors. Existing direct unit
coverage is limited, so the new integration test is a prerequisite, not an
after-the-fact assertion.

### Milestone 6 — Integrate canonical handling into master persistence boundary

Treat `_merge_into_all_jobs` as a legacy compatibility/storage boundary. It consumes
the projected Indeed records from Milestone 5 and continues to write JSON. Do not
make it accept/domain-serialize dataclasses, change pruning, refresh `first_seen`,
or replace `_same_job` in this milestone.

Extend the integration test to prove the pilot projection passes through
`_merge_into_all_jobs`, preserves master insertion `first_seen`, preserves existing
arbitrary true/false downstream fields on duplicates, accumulates `duplicate_urls`,
and retains the 30-day behavior exercised by existing clock-controlled tests. Add
a spy/contract assertion that notification input and source output use projected
legacy dictionaries, not domain objects.

Document in code only where needed that the current merge result is legacy
compatibility behavior and does not assign an Accepted identity outcome. If a
canonical decision would disagree with current `_same_job`, preserve current output,
record it here, and stop any attempt to route canonical identity into persistence.
Replacing master deduplication needs separate fixtures/evaluation and later scope.

### Milestone 7 — Expand to remaining current producers only where safe

After the Indeed pilot and master-boundary tests pass, record this classification
in Progress/Outcomes:

| Producer group | This ExecPlan | Reason |
|---|---|---|
| Indeed `save_indeed_results` | Migrate as the sole pilot. | Representative rich record, stable identity signal, thin saver, no-network synthetic validation. |
| LinkedIn, Google Jobs, HiringCafe | Retain current flow behind existing dictionary/JSON compatibility boundary. | Provider-specific enrichment/link behavior and zero-data preservation need dedicated fixtures before canonical adoption. |
| Glassdoor, ZipRecruiter | Retain current flow; adapter compatibility fixtures may cover their JobSpy-shaped records, but do not enable another production path. | Shared shape reduces future work, but local outputs/tests provide little validation and migration is not required for foundation. |
| Priority/Greenhouse/Workday direct probes | Defer. | Mixed legacy source/ATS meaning and priority envelope/path require focused contract work. |
| CalCareers, USAJOBS, NEOGOV, CalOpps, CSU | Defer. | Manual/legacy paths and source-specific deadline/telework fields require source fixtures; CSU semantics are tested at adapter level without migrating its producer. |
| Legacy `save_results` | Defer and preserve. | Its three-key envelope and missing master/notification behavior are explicit compatibility exceptions. |

Do not expand production integration merely because another record passes the
generic adapter tests. Expansion requires source-specific no-network fixtures and
an explicit update to this active plan.

### Milestone 8 — Compatibility and regression validation

Run focused domain, adapter, pilot and legacy tests, then the full suite. Compare
representative projected dictionaries and envelopes exactly. Inspect the diff for
scope, imports, accidental format changes, new dependencies and generated output.

There is no browser automation in `tests/`; prove the dashboard contract
mechanically by asserting filenames/envelopes/raw URLs and by reviewing `SOURCES`,
`loadJobs`, `enrich`, `_jobKey`, `jobFreshMs`, `slimJob` and `save` against projected
keys. If practical, serve the unchanged repository locally and manually load the
dashboard without editing state; record that as manual evidence, not an automated
guarantee. Do not require live board calls, Pushover delivery, model calls or remote
workflow execution to close this milestone.

Update this plan's actual results, [CURRENT_STATE.md](../../CURRENT_STATE.md), and
the CURRENT section of [ARCHITECTURE.md](../../../ARCHITECTURE.md) only if the
implemented boundary genuinely changes it. Update the Accepted design only for a
genuine semantic issue requiring user review. ROADMAP normally remains unchanged.

## Concrete Steps

Run commands from the repository root. Use the active project environment; the
commands below assume `python` has dependencies from `tests/requirements-dev.txt`.
Keep `PYTHONDONTWRITEBYTECODE=1` and disable pytest's cache provider to avoid
unrelated repository artifacts.

### Milestone 1 steps — executable domain contract

- **Files/functions:** add `canonical_job.py` with frozen domain value objects,
  validation hooks, `IdentityOutcome`, identity evidence/result and the conservative
  evaluation entry point. Add the initial construction tests to
  `tests/test_canonical_job_domain.py`.
- **Tests:** write failing tests first for valid/minimal construction, unknowns,
  scoped source/ATS identity, link roles, opaque canonical identity, and invalid
  observation ordering; then implement only enough contract to pass.
- **Command:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_canonical_job_domain.py -q -p no:cacheprovider
  ```

- **Expected:** initial import/contract failures, then a clean domain-test result;
  no production caller and no filesystem/network side effect.
- **Stop:** a representation forces provider precedence, a Company entity, role
  taxonomy, database/storage shape or another unapproved semantic.
- **Recovery:** revert only the additive module/test portion that is internally
  inconsistent; record evidence before revising this plan or Accepted design.

### Milestone 2 steps — validation and invariant tests

- **Files/functions:** extend `tests/test_canonical_job_domain.py` and the validation/
  identity evaluator in `canonical_job.py`.
- **Tests:** add named cases for provenance preservation, source/application links,
  unknown/null, time ordering, deadline conflicts, source versus ATS namespace,
  candidate/derived exclusion, fuzzy-title-only non-equivalence, deterministic
  equality, composite possible match and every listed material contradiction.
- **Command:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_canonical_job_domain.py -v -p no:cacheprovider
  ```

- **Expected:** all approved invariants pass without numeric similarity thresholds;
  test names reveal the behavioral rule they encode.
- **Stop:** an assertion derives a new semantic from implementation convenience or
  weakens an Accepted invariant. Keep the human-approved rule and pause the code.
- **Recovery:** retain Milestone 1's valid value objects, revert the disputed
  evaluator/test case, and log the exact design boundary.

### Milestone 3 steps — legacy input transformation

- **Files/functions:** add `job_compat.py` transformation/context and
  `tests/test_canonical_job_compat.py`; add compact fixtures only if exact records
  become unreadable inline.
- **Tests:** transform representative Indeed, sparse, master, CSU-deadline and
  unknown-valued dictionaries. Assert field provenance, compatibility extras,
  non-fabricated observation/ATS values and exclusion of workflow fields from facts
  and identity.
- **Command:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_canonical_job_domain.py tests/test_canonical_job_compat.py -q -p no:cacheprovider
  ```

- **Expected:** transformations preserve evidence and ambiguity; no legacy input or
  output file is mutated.
- **Stop:** the adapter would need to invent observation time, infer ATS provider
  from a mixed source label, discard ambiguous data or reinterpret candidate state.
- **Recovery:** keep the domain module; revert or isolate the unconnected adapter
  change and record the problematic legacy record shape.

### Milestone 4 steps — compatibility projection

- **Files/functions:** add projection functions in `job_compat.py`; extend
  `tests/test_canonical_job_compat.py` and reviewed fixtures.
- **Tests:** exact dictionary round trips for key presence and values; aliases,
  nullable/false/empty distinctions, raw URLs, mixed `ats`, timestamps,
  `duplicate_urls`, deadline aliases and arbitrary extensions; assert canonical-only
  fields do not leak.
- **Commands:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_canonical_job_compat.py tests/test_schema_validation.py -q -p no:cacheprovider
  git diff -- schema/jobs.schema.json tests/fixtures
  ```

- **Expected:** projection/golden and existing schema-fixture tests pass;
  `schema/jobs.schema.json` remains the legacy contract and is unchanged absent a
  separately reviewed finding.
- **Stop:** projection cannot reproduce a required compatibility value without
  violating accepted semantics; preserve it in compatibility extras and pause if
  exact output is still impossible.
- **Recovery:** production is not connected yet; revert projection independently
  while retaining transformation evidence.

### Milestone 5 steps — Indeed pilot

- **Files/functions:** minimally edit `scrape_jobs.py::save_indeed_results` and one
  small named helper; add `tests/test_canonical_job_integration.py`.
- **Tests:** patch delivery/time and use `tmp_output_dir`; assert source envelope,
  current/new job lists, raw identities, notification input, master fields and score
  URL key before/after canonical round trip. Do not invoke JobSpy.
- **Command:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_canonical_job_integration.py tests/test_work_arrangement_classification.py -q -p no:cacheprovider
  ```

- **Expected:** synthetic Indeed records cross the boundary with compatible external
  output and no live network or real output write.
- **Stop:** integration changes JSON fields/envelope, current newness, raw URL keys,
  work labels, notification identity, formatting or ordering.
- **Recovery:** remove the helper call from `save_indeed_results`; additive modules
  and evidence tests require no data rollback.

### Milestone 6 steps — master persistence boundary

- **Files/functions:** extend `tests/test_canonical_job_integration.py` and
  `tests/test_master_jobs_file_merge.py`; normally leave `_merge_into_all_jobs`
  unchanged. If a narrow seam is necessary, log it before editing.
- **Tests:** projected Indeed dictionaries reach the master; insertion
  `first_seen`, field preservation, false-valued extensions, `duplicate_urls`,
  retention and projected notification dictionaries match legacy behavior.
- **Command:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_canonical_job_integration.py tests/test_master_jobs_file_merge.py tests/test_job_deduplication.py -q -p no:cacheprovider
  ```

- **Expected:** current master tests and new boundary tests pass; real `output/` is
  untouched and no canonical identity outcome drives legacy merging.
- **Stop:** integration requires replacing `_same_job`, changing retention,
  refreshing `first_seen`, serializing domain objects or rewriting existing data.
- **Recovery:** restore `_merge_into_all_jobs` and the Indeed caller to their last
  passing form; retain legacy persistence until a later evaluated migration.

### Milestone 7 steps — producer expansion decision

- **Files/functions:** no additional production migration by default. Update this
  plan's Progress/Surprises/Outcomes with the verified producer classification;
  adapter fixture coverage may be extended in `tests/test_canonical_job_compat.py`.
- **Tests:** optionally add representative dictionary-only cases for another JobSpy
  shape or legacy deadline shape; these do not authorize another saver integration.
- **Command:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_canonical_job_compat.py tests/test_canonical_job_integration.py -q -p no:cacheprovider
  ```

- **Expected:** Indeed remains the sole production pilot; all other producer groups
  have an evidence-based migrate/retain/defer disposition recorded.
- **Stop:** a proposed second integration lacks source-specific fixtures or expands
  into provider fetching/parsing. Defer it rather than inferring safety from shape.
- **Recovery:** remove any unapproved second caller; adapter-only fixture coverage
  can remain if it encodes accepted semantics and current evidence.

### Milestone 8 steps — regression validation and closure

- **Files/functions:** all affected code/tests plus this plan and handoff/catalog;
  update Architecture CURRENT only if the implemented boundary genuinely changes.
- **Tests/checks:** focused contract tests, affected legacy tests, full suite,
  JSON/fixture equality, documentation links, diff/status, output immutability and
  static consumer review. Record automated versus manual/operational limits.
- **Commands:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_canonical_job_domain.py tests/test_canonical_job_compat.py tests/test_canonical_job_integration.py -v -p no:cacheprovider
  PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/ -q --ignore=tests/local -p no:cacheprovider
  git diff --check
  git status --short
  git diff -- canonical_job.py job_compat.py scrape_jobs.py tests schema/jobs.schema.json docs
  ```

- **Expected:** focused and full suites pass; no generated output, configuration,
  workflow, external dependency or out-of-scope subsystem changes; actual results
  and limitations are recorded before the plan moves to completed.
- **Stop:** any unexplained regression, shape/key/value drift, test needing live
  network, out-of-scope diff or unrecorded acceptance gap. Do not close the plan.
- **Recovery:** restore the Indeed caller first to disable adoption, return to the
  last passing milestone, update the active handoff and leave the plan Active.

## Test Strategy

### Human-approved behavioral rules

The Accepted design is authoritative for test intent: one Job is an opening rather
than a URL; provenance survives; source/ATS/canonical identities differ; source and
application links differ; unknown remains unknown; observation times differ from
posting/verification; deadline evidence and conflict remain visible; explicit work
terms are provenance and normalized work is derived; compensation observations
support but differ from comparable salary; candidate/workflow state cannot affect
identity; and identity outcomes use conservative evidence tiers with contradictions
blocking `AUTO_MERGE`.

These rules are not inferred from whichever classes are easiest to implement.
Changing them requires design review, not a test update inside this plan.

### Agent-authored executable tests

- **Unit tests:** domain constructors/validation, time ordering, scoped IDs, link
  roles, deadline/compensation observations, and identity evidence outcomes.
- **Contract tests:** legacy transformation/projection exactness, unknown/key
  presence, no canonical-only leakage, current aliases, and deterministic exclusion
  of candidate/derived data from identity.
- **Integration tests:** Indeed saver → domain → projection → existing source/master/
  notification boundaries, all using temporary output and patched delivery/time.
- **Regression tests:** existing dedupe, merge, schema fixture, work arrangement,
  LinkedIn parsing/partition and complete test suite.
- **Static/manual consumer checks:** dashboard required keys/URLs and notifier/agent
  raw URL behavior. No browser automation exists; record any manual load separately.

Prefer test-first for identity, unknown/null, provenance, timestamp, compatibility
serialization and contradiction behavior. Keep legacy tests when target and legacy
semantics differ; do not rewrite them to make new types pass.

## Validation and Acceptance

Record expected commands and later actual results separately. At plan creation the
expected commands are in Concrete Steps; **actual results are pending**.

Final acceptance requires all of the following:

1. Canonical Job, source observation, scoped identity and identity outcome semantics
   exist in executable Python code with no new external dependency.
2. Provenance survives legacy transformation and remains traceable from preferred
   compensation/deadline/application projections.
3. Compatibility projection preserves in-scope current dictionary keys/values and
   existing JSON envelopes/filenames for the pilot.
4. Legacy `url`, mixed `ats` and `first_seen` semantics are not silently redefined.
5. Unknown/absent/null/false/empty distinctions are preserved where current records
   expose them; missing salary is never zero and missing remote is never false.
6. `first_seen_at <= last_seen_at` validation and posting/observation separation are
   covered by tests; no unsupported last-seen value is invented.
7. Source versus application URL roles, equal links and multiple destinations are
   covered without making preferred link identity.
8. Candidate-specific fields and role/work derived values cannot change canonical
   identity; source work wording remains provenance.
9. Fuzzy title similarity alone cannot produce `AUTO_MERGE`.
10. Material identity contradictions block deterministic auto-merge; scoped source
    and ATS equality cases are qualified by namespaces and absence of contradiction.
11. The synthetic Indeed pilot round-trips through canonical and compatibility
    layers and reaches current source/master/notification paths with compatible
    observable output.
12. Focused tests, affected legacy tests, schema fixture tests and the full existing
    suite pass; actual versions/results and limitations are recorded here.
13. No Postgres/Supabase, Notion, live verifier, broad URL resolver, Phase 2 feature,
    Company entity, numeric similarity threshold or broad refactor is introduced.
14. Real `output/` is unchanged by tests; CLI flags and workflows are unchanged.
15. Progress, discoveries, decisions, CURRENT_STATE and implemented architecture
    truth are updated before the plan moves to `completed/`.

Operationally unverified items must be stated: live board reachability, remote
Actions/Python 3.11, actual Pushover delivery, model calls, browser/localStorage
runtime and deployed JSON remain outside no-network local acceptance.

## Idempotence / Failure / Recovery

There is no external migration, database write or bulk rewrite in this plan. Domain
and adapter tests are repeatable. `tests/conftest.py` redirects scraper output; new
integration tests must also patch notifications and use fixed clocks, so reruns do
not modify real outputs or external services.

Adoption is intentionally one caller deep. Before Milestone 5, modules are additive.
After Milestone 5, reverting the helper call in `save_indeed_results` restores the
current path without data conversion. `_merge_into_all_jobs` continues to store
legacy dictionaries, so disabling the pilot requires no migration or interpretation
of previously written canonical payloads.

Interruption protocol:

1. Finish or revert the smallest current step; never leave the Indeed caller using
   a partly implemented adapter.
2. Run the focused tests for the last completed milestone.
3. Update Progress, Surprises and Decision Log with exact files/commands/results.
4. If pilot tests fail, remove the production call first; preserve failing fixtures
   only when they document a real compatibility issue.
5. Reinspect `git status` and confirm real `output/` hashes/status are unchanged.

Rollback is not assumed trivial if `_merge_into_all_jobs` or output semantics are
changed. Such a change is a stop condition under this plan; restore the legacy
boundary before continuing. Incomplete adoption must never write canonical-only
fields, reinterpret legacy timestamps or change consumer keys.

## Interfaces and Dependencies

| Interface | Direction and contract |
|---|---|
| Current scraper dictionary | Input to `job_compat`; source-specific, incomplete, mutable, mixed legacy semantics. |
| Adapter context | Supplies collection source, optional actual observation time and canonical-ID assignment; never guesses unavailable evidence. |
| Canonical domain objects | Internal validated values from `canonical_job.py`; no direct JSON/output consumer in this milestone. |
| Compatibility projection | Canonical composition + preserved extras → current-compatible dictionary without canonical-only leakage. |
| `save_indeed_results` | Sole production pilot caller of the adapter/projection. |
| `save_jobs_output` | Remains legacy common writer/newness/notifier boundary accepting dictionaries. |
| `_merge_into_all_jobs` | Remains JSON-primary legacy merge/retention boundary accepting projected dictionaries. |
| `schema/jobs.schema.json` | Existing legacy single-record declaration and fixture test; not canonical executable authority. |
| Source/master JSON | Existing filenames/envelopes and raw keys consumed by dashboard/notifier/agent. |
| Dashboard | Reads raw URLs/current fields; no code change planned. |
| Notifications | Receives projected dictionaries and retains company/title identity and raw links. |
| Legacy AI | Reads master/current fields and URL-keyed scores; no code change planned. |

Dependencies remain the Python standard library plus current test tooling. Do not
add a validation/modeling package. If implementation proves a new dependency
necessary, record the evidence and stop for plan review before editing dependency
files.

## Outcomes & Retrospective

Status: Pending implementation.

At closure, replace this placeholder with:

- the executable boundaries and authoritative module names actually delivered;
- the exact Indeed pilot call path and whether any master seam changed;
- focused/full test commands, versions, counts, results and verification limits;
- compatibility findings for JSON, dashboard keys, notification identity and
  legacy URL-keyed scores;
- deviations from this plan and why they were safe;
- remaining producer classification and any source-specific fixtures still needed;
- residual design/technical debt and unresolved operational verification;
- the next recommended milestone, without pulling Postgres or later intelligence
  into this completed record.

Move this file to `docs/exec-plans/completed/` only after all acceptance criteria
are met, actual validation is recorded, documentation truth is updated, and no
required work remains. If cancelled or superseded, retain the plan with an explicit
status/reason rather than implying delivery.
