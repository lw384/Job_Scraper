# Canonical Job Model

Status: Accepted
Classification: TARGET DESIGN
Last updated: 2026-09-15

This document owns the accepted target domain semantics for the canonical Job
model. Accepted means approved target semantics, not implemented behaviour or an
executable contract. Executable conformance must later be established through
code, schema and tests. **CURRENT** paragraphs record inspected repository
behaviour; **TARGET** identifies approved target design; **DERIVED** identifies
conclusions rather than observed facts; **DEFERRED** identifies representation or
implementation decisions not made here. Section 15 records the review resolution.

## 1. Purpose

Define what one Job means and how its facts relate to observations, identity,
verification, classifications, and personal analysis. The central entity should
represent one real-world job opening, even when several collectors encounter it.

**CURRENT:** collectors produce different dictionaries rather than one enforced
domain model. JobSpy records contain remote, currency, employment-type and direct
URL fields; CSU records include a summary and `closing_date`; source snapshots and
the master differ in discovery timestamps. Evidence:
[scrape_jobs.py](../../scrape_jobs.py), `_ingest_jobspy_df`,
`_parse_csucareers_listing`, `save_jobs_output`, `_merge_into_all_jobs`.

**CURRENT:** the declared [job schema](../../schema/jobs.schema.json), persisted
records, scraper identity, browser clusters, and notification identity are not one
consistent contract. The dashboard derives roles, seniority, work arrangement and
scores in [triage.html](../../triage.html), `enrich`. Section 3 names the specific
discrepancies; section 12 identifies compatibility surfaces.

**TARGET:** establish shared semantic boundaries before selecting an executable
model or persistence layout. Existing JSON and consumers should remain operational
until explicit replacements are implemented and validated, following
[the roadmap](../roadmap.md). This design does not make the current JSON schema the
permanent internal domain representation.

## 2. Scope and Non-goals

**TARGET scope:** job-domain boundaries; factual attributes; source/provenance
separation; canonical, source and ATS identity semantics; time and unknown-value
semantics; invariants suitable for later executable contracts; and compatibility
expectations for current JSON consumers.

**Excluded:** physical PostgreSQL/Supabase schema, migrations, storage parity
implementation, migration/recovery mechanics, Notion schema or synchronization
ownership, scoring formulas, Daily Priority, eligibility processing, skill
extraction, interview preparation, ATS-specific verifier implementation, and
detailed Phase 1 sequencing. Those systems are discussed only enough to locate
their domain boundaries. No SQL, ORM, dataclasses, endpoints, or file moves are
specified. Substantial implementation belongs in a future ExecPlan under
[PLANS.md](../../PLANS.md), after appropriate design decisions.

This document explains semantics and design choices. A future machine-readable
model/schema should own executable field constraints; generated references should
derive from it. Its format and repository location remain **DEFERRED**. Existing
`schema/jobs.schema.json` currently expresses a declared JSON-record contract,
not an implemented future canonical model.

## 3. Current Problems and Constraints

### Schema/output consistency — CURRENT

- [schema/jobs.schema.json](../../schema/jobs.schema.json) requires `url`, `title`,
  `company`, `ats`, and `first_seen` on a single record. It allows extra properties
  and defines no JSON envelope. `save_jobs_output` writes original source records;
  `_merge_into_all_jobs` stamps newly inserted master copies. Thus source records
  do not receive master `first_seen` through that operation.
- `_coerce_bool` returns `None` for empty/missing input; `_ingest_jobspy_df` and
  Google normalizers can persist that as `is_remote`. The schema permits only a
  boolean when this property exists. These are different contracts, not evidence
  that unknown remote status is false.
- Read-only inspection on 2026-09-15 confirmed 24 null remote values in 438 local
  master jobs, and four Google source jobs with missing `first_seen` and null
  `is_remote`. These are dated local observations, not remote health claims.
  Evidence: [all_jobs.json](../../output/all_jobs.json),
  [google_jobs.json](../../output/google_jobs.json).
- `_parse_csucareers_listing` emits `closing_date` and summary `description`.
  The schema does not declare `closing_date`; its description says government
  descriptions are absent. Permissive extra properties allow the deadline field
  without defining its semantics.
- [test_schema_validation.py](../../tests/test_schema_validation.py) validates
  synthetic fixture records, with a required-field-only fallback when jsonschema
  is absent. It does not validate persisted outputs. The inspected runtime
  producer/consumer paths do not invoke this schema.

### Identity fragmentation — CURRENT

| Consumer or operation | Current meaning of identity | Evidence |
|---|---|---|
| Collector row identity / source newness | `_job_identity(url)` extracts selected posting IDs or normalizes host/path. `save_jobs_output` compares against the previous source snapshot, not master membership. | `scrape_jobs.py`, `_ingest_jobspy_df`, `_load_prev_ids`, `save_jobs_output` |
| Master merge | URL and normalized-ID indexes, including `duplicate_urls`, followed by company/title/location or description heuristics. The retained record keeps its primary URL. | `scrape_jobs.py`, `_job_urls`, `_same_job`, `_dedupe_master_jobs`, `_merge_into_all_jobs` |
| Dashboard | Exact-URL union in fixed source order, followed by transitive pairwise content/URL clustering. Richness and freshness select a primary card. | `triage.html`, `SOURCES`, `loadJobs`, `_jobKey`, `_shouldMerge`, `dedupe`, `_mergeCluster` |
| Notifications | Lowercased company and title with non-alphanumeric characters removed, ignoring URL, location and source. | [notify.py](../../notify.py), `_identity`, `notify_new_jobs` |
| AI scores and browser annotations | Raw posting URL keys. Browser cluster consolidation handles selected triage statuses; notes/stars/timelines are not generally merged across the cluster. | [triage_agent.py](../../triage_agent.py), `main`; `triage.html`, state initialization, `enrich`, `_mergeCluster` |

The scraper's generic URL fallback drops all query parameters. For example,
CalCareers URLs distinguished only by `JobControlId` collapse to the same host/path
identity. `_job_urls` does not include `direct_url`. An equal normalized URL can
therefore bypass company/content checks; it is not universal proof of equivalence.
Evidence: `scrape_jobs.py`, `_job_identity`, `_job_urls`, `_same_job`;
[test_job_deduplication.py](../../tests/test_job_deduplication.py),
`test_same_url_means_same_job`.

`_merge_duplicate_job` fills missing description/salary and selected auxiliary
fields, then retains alternate URLs. It does not preserve all competing source
values or update non-empty old content. Its truthiness check skips incoming
`is_remote=False`. This differs from preserving false-valued fields already on a
surviving master record, which
[test_master_jobs_file_merge.py](../../tests/test_master_jobs_file_merge.py)
exercises. Neither contract defines future canonical merge confidence.

### Source versus canonical facts — CURRENT

`_ingest_jobspy_df` keeps `job_url` as `url` and `job_url_direct` as `direct_url`.
`_normalize_serpapi_google_job` instead chooses an apply link as `url` when present
and repeats it in `direct_url`, with share/link fallbacks. CSU also sets both URL
fields to the same value. One field consequently serves several roles depending
on the producer. Equal values are compatible with distinct semantics, but a board
listing URL does not itself prove a direct application destination.

`ats` is currently a source label: the schema enum and producer values include
LinkedIn, Indeed, GoogleJobs and HiringCafe alongside Greenhouse and Workday.
It does not consistently identify the employer's ATS. Evidence: schema `ats`,
`_ingest_jobspy_df`, Google normalizers, curated probes in `scrape_jobs.py`.

### Derived versus factual data — CURRENT

`classify_work_arrangement` and `_ensure_work_arrangement` persist inferred labels
in job dictionaries. Generic remote text becomes `Remote in-state eligible`;
hybrid text becomes `Telecommute eligible`. These heuristics are exercised by
[test_work_arrangement_classification.py](../../tests/test_work_arrangement_classification.py),
but do not establish candidate eligibility or permitted employment geography.

`triage.html`, `classifyRole`, `classifySeniority`, `classifyWorkArrangement`,
`parseSalary`, and `enrich`, derive browser attributes. `applyConfig` rebuilds role
buckets from `role_categories.terms`; they are configurable display classifications,
not a shared canonical taxonomy. `scrape_jobs.py`, `_load_config`/`_deep_merge`,
loads personal overrides at import time. Configuration-driven discovery or browser
classification does not change what constitutes an opening.

Salary values also mix extraction and formatting: `format_salary` uses dollar
symbols while `_ingest_jobspy_df` retains a separate currency field. Dashboard
salary parsing annualizes text without currency conversion. Evidence:
`scrape_jobs.py`, `format_salary`; `triage.html`, `_annualMult`, `parseSalary`.
The target must distinguish an employer's stated compensation from a calculated
comparison value without fixing those implementations in this task.

## 4. Terminology and Domain Boundaries

**TARGET conceptual responsibility map**, not physical tables or classes:

```text
Raw Source Record
        ↓
Source / Provenance Observations
        ↓
Canonicalization / Identity
        ↓
Canonical Job
        ├── preferred factual view
        ├── observation metadata
        ├── preferred application link projection
        ├── preferred compensation/deadline projections
        │
        ├── associated Verification Assessment
        │     LIVE / CLOSED / UNKNOWN
        ├── associated Derived Classification
        │     role family / seniority / normalized work arrangement
        └── associated Candidate / Application Intelligence
              eligibility / Fit Score / Daily Priority
              skill/evidence gaps / interview preparation / workflow state
```

Associated assessments, classifications and personal intelligence are separate
responsibilities referencing the Job. Their inclusion in this map does not place
them in the factual Job core.

### 4.1 Raw Source Record

**TARGET:** one source-specific record as observed by a collector, together with
its observation context. It may be incomplete, duplicated, malformed or inconsistent
with another source. Observation is not acceptance of every value as canonical.

**CURRENT distinction:** collector dictionaries are already filtered/normalized
and sometimes truncated; they are not guaranteed lossless raw upstream payloads.
Evidence: `_ingest_jobspy_df`, `_normalize_serpapi_google_job`,
`_parse_csucareers_listing`. Do not rename current snapshots “raw” and imply data
they do not contain. Exact raw-payload preservation and retention are **DEFERRED**.

### 4.2 Canonical Job

**TARGET:** one real-world job opening described through accepted factual
observations. It is not a scraped URL, collector result, candidate assessment or
application. Several advertisements may describe the same opening; identical
titles at one company can describe distinct openings. One advertisement may cover
multiple vacancies, so this does not assert that one Job equals one hiring seat.

Canonical facts are a selected factual view with traceable observations, not an
assertion of perfect employer truth. Changes to title, content, deadline or links
should not alone create a new identity. Unresolved evidence should remain visible;
incomplete records must not gain fabricated facts simply to fit a model.

### 4.3 Job Source / Provenance

**TARGET:** the association between an opening and one or more source records and
their observations. It owns collection source, source-specific identity, source
URLs, observed values and observation times. Canonicalization should preserve
these associations and the evidence behind selected facts. This is a responsibility
boundary, not a database-table proposal.

### 4.4 Verification State

**TARGET, accepted conceptual vocabulary:** `LIVE / CLOSED / UNKNOWN`, as recorded
in [the roadmap](../roadmap.md). A separate verification assessment describes
availability supported by evidence at a check time:

- `LIVE`: sufficient evidence that the opening is currently accepting applications.
- `CLOSED`: sufficient evidence that it is no longer accepting applications.
- `UNKNOWN`: no sufficient current evidence for either conclusion.

An assessment should retain check time, checked destination and supporting evidence
conceptually; exact evidence requirements, freshness and conflicting-source
aggregation are **DEFERRED**. Failed requests, missing deadlines, old discovery
times and dashboard dismissal do not establish closure. An observation timestamp
is not a verification timestamp. **CURRENT:** the inspected scraper merge performs
discovery-based pruning, not this three-state verification (`_merge_into_all_jobs`).

### 4.5 Derived Classification

**DERIVED / TARGET:** normalized role family, seniority, inferred work arrangement
and comparable system classifications. They express interpretation of facts;
reclassification should not change Job identity. Employer wording remains evidence.
Role classification may be associated with or referenced from a Job as a separate
derived result/view; it must not be embedded in the factual core for convenience.
Taxonomy, versioning and persistence representation belong to Phase 2 and remain
**DEFERRED**. For work arrangement, preserve explicit employer/source work wording
in provenance and normalize it into a separate derived classification, such as
REMOTE / HYBRID / ONSITE / UNKNOWN or a future equivalent. Exact enum names and
taxonomy are **DEFERRED**. Remote wording does not establish unrestricted geography
or candidate eligibility.

### 4.6 Personal / Candidate-specific Analysis

**TARGET boundary:** eligibility, Fit Score, Daily Priority, skill/evidence gaps,
interview preparation, notes, shortlist and application/Notion workflow state
remain outside canonical Job facts and identity. They depend on a candidate, user
action, policy or analysis version. Fit Score and Daily Priority are separate
accepted product concepts; no formulas or persistence ownership are selected here.

## 5. Canonical Job Identity

### 5.1 Canonical Identity

**TARGET:** two records share canonical identity when evidence supports that they
describe the same employer opening, rather than merely similar roles. A canonical
identifier should remain stable as observations, classifications and preferred
links change. It should not be recomputed from mutable factual values alone.

Identity assignment and confidence in a proposed match are different concerns.
The evidence-tier semantics in section 5.4 are accepted. The identifier generation
algorithm, merge/split handling and numeric similarity thresholds are **DEFERRED**.
A reopened or reposted advertisement might describe the same opening or a new
requisition; neither URL reuse nor elapsed time alone settles that distinction.
The evidence tiers and contradiction safeguards in section 5.4 apply to this case;
identifier-reuse evaluation details remain deferred, not an implicit retention rule.

### 5.2 Source Identity

**TARGET:** an identifier scoped to a source's posting namespace. A board posting
ID can distinguish records on that board without proving cross-source equivalence.
Tenant/employer scope matters where identifiers are not globally unique. An
observation of a posting is distinct from its source posting identity: repeated
observations may update the facts associated with that identity.

URLs may be a provisional source locator when no ID is known. Query parameters
can contain either tracking or material posting identity; stripping them all is
not a universal rule. Preserve the observed URL and identifier evidence even when
normalizing a locator. **CURRENT examples:** `_job_identity` extracts numeric
LinkedIn IDs and Indeed `jk`, but has a generic host/path fallback.

### 5.3 ATS Identity

**TARGET:** an employer application-system posting/requisition identifier, qualified
by provider and relevant tenant/employer namespace. Workday, Greenhouse, Lever,
Ashby or equivalent identifiers may provide strong cross-source evidence when
reliably observed. They are examples of signals, not a promise of current collector
coverage or a provider-specific algorithm.

An aggregator's label is not an ATS identity, and an unqualified numeric ID is not
necessarily globally unique. The same ATS namespace and opening identifier can be
strong evidence; conflicting authoritative identifiers should not be erased by
title similarity. Exact requisition/posting relationships, identifier-reuse
evaluation and provider-specific precedence remain **DEFERRED** within the accepted
evidence-tier policy. Current heuristics do not establish these target details.

### 5.4 Duplicate / Equivalence Semantics

**TARGET accepted evidence tiers:**

| Outcome | Evidence and treatment |
|---|---|
| AUTO_MERGE | Strong deterministic or independently reliable evidence supports one opening, with no material contradiction. Examples include repeated observations of the same scoped source posting, a reliably established shared ATS/provider + tenant/employer namespace + opening ID, or an equally strong deterministic relationship. These are evidence categories, not unconditional provider rules. |
| POSSIBLE_MATCH / REVIEW | Strong composite agreement, such as normalized employer, strongly compatible title/location, substantial content agreement or application-link evidence, without reliable shared opening identity. Retain possible-match evidence for review; a high similarity score alone must not automatically collapse records. |
| KEEP_SEPARATE | Evidence is insufficient or materially contradictory. Fuzzy title similarity alone is never sufficient for canonical equivalence. |

Material contradiction can block AUTO_MERGE even when several similarity signals
agree. Safeguards must consider conflicting scoped ATS/requisition IDs, clearly
incompatible employer identity, materially incompatible locations for a
location-specific posting, materially different requisition content, and evidence
that two simultaneous openings exist separately. Preserve contradictory evidence;
do not erase it by selecting a richer or newer record.

Multiple source records may resolve to one Job. Merging must preserve provenance
and must not make a display-primary URL authoritative identity. Pairwise probable
similarities do not prove a transitive cluster; contradictions across the whole
proposed group must remain assessable. Exact group-validation algorithms,
identifier-reuse evaluation and reversible merge/split correction are **DEFERRED**.
Numeric similarity thresholds belong to later implementation/evaluation with
fixtures and real data; none are specified here. The current `_same_job`
thresholds and dashboard transitive clustering are CURRENT implementation evidence,
not the accepted target evidence policy.

## 6. Canonical Job Record Concepts and Ownership

Inclusion means that a concept is relevant to the canonical Job domain and its
boundaries, not that it must be stored directly as a field on Canonical Job. The
owner column distinguishes the factual core, canonical observation metadata,
provenance/link evidence, convenience projections and derived classifications.
This is not a required-field, serialized-name or type specification. **TARGET**
ownership/meaning is accepted; **DERIVED** values are conclusions; exact deferred
representations do not reopen accepted semantic ownership. Current aliases are
named explicitly and do not imply target semantics are implemented.

| Concept | Meaning | Domain owner | Status | Unknown/null meaning |
|---|---|---|---|---|
| title | Employer/source-stated role title; preferred factual wording with traceable alternatives. Current alias: `title`. | Canonical facts, supported by source observations. | TARGET | No reliable title observed; do not invent a classification as the title. |
| company | Employer identified by the advertisement. Current alias: `company`; JobSpy can substitute `Unknown`. | Canonical factual core: normalized employer text in Phase 1; source wording remains provenance. No separate Company entity in Phase 1. | TARGET | Employer unknown; the placeholder `Unknown` is not an employer identity. |
| description | Observed JD/content, with origin and completeness retained; not an AI summary presented as source text. Current alias: `description`, sometimes a listing summary. | Canonical preferred content plus provenance. | TARGET | Content unavailable/not observed; empty does not mean the role has no requirements. |
| location | Employer-stated location(s) and geographical restrictions. Current alias: `location`. | Canonical factual view plus source wording; exact normalization deferred. | TARGET | Location unresolved; not proof of remote, global hiring or no restrictions. |
| salary | Employer/source compensation statement, including currency and interval when observed. Current aliases: `salary`, `salary_currency`, `salary_source`. | Provenance owns compensation observations; Canonical Job may expose a traceable preferred normalized/current compensation view. Annualized/comparable values remain DERIVED. Exact structure/normalization is deferred. | TARGET | Compensation unknown, not zero or unpaid. |
| posted_at | Employer/source-stated posting date/time with known precision. Current alias: source-varying `date_posted`. | Canonical factual view plus original source value. | TARGET | Posting time unknown; discovery time must not substitute as employer posting time. |
| application_deadline | Employer-stated application cutoff, possibly changed later. Current CSU alias: `closing_date`; no shared `application_deadline` field exists in inspected producers. | Preferred factual deadline projection backed by trusted temporal source observations; accepted authority/recency principles in section 8.2, exact rules deferred. | TARGET | No established cutoff; not evidence of rolling recruitment. |
| first_seen_at | Earliest accepted actual observation of this opening by this system. Current `first_seen` instead records new master insertion. | Canonical observation metadata derived from provenance, not employer facts. | TARGET | No reliable historical observation time; do not backdate from posting text. |
| last_seen_at | Latest accepted actual observation of this opening by this system. No corresponding update exists in the current master merge. | Canonical observation metadata derived from provenance. | TARGET | Latest observation unknown; neither LIVE nor CLOSED follows. |
| direct_url | Observed direct application destination, distinct from board/source URL. Current alias: `direct_url`, sometimes repeated in `url`. Reliability evidence remains separate. | Provenance/link evidence owns application destinations; Canonical Job may expose one preferred application link projection. Selection/reliability algorithms are deferred; no physical Link entity is required. | TARGET | No reliable direct destination known; source URL may still be available. |
| ats | Employer ATS/provider, when supported by evidence. Current `ats` is instead a mixed source label and must retain that meaning in compatibility output. | ATS/application provenance; not a replacement for collection source. | TARGET | Provider unknown, not absence of an ATS. |
| ats_job_id | Scoped employer ATS posting/requisition identifier, not a board ID or canonical ID. No shared field contract exists in inspected producers/schema. | ATS identity evidence associated with provenance. | TARGET | Identifier not established; title/URL similarity does not fabricate one. |
| normalized work arrangement | System-normalized interpretation of explicit work terms or inferred signals. Current aliases: persisted `work_arrangement`, browser `_work`. | Separate derived classification referencing the Job; explicit work wording/evidence remains provenance. Exact taxonomy is deferred. | DERIVED | No supported classification; unknown must not become on-site/ineligible. |

Selection of preferred title/content/location/posting values must remain traceable.
Phase 1 uses normalized employer text and retains differing source employer
wording. Company alias resolution, legal entities and parent/subsidiary modelling
remain deferred beyond Phase 1; no separate Company entity is introduced.

Compensation observations remain provenance. A preferred normalized/current
compensation view is allowed for downstream filtering/comparison, with its source
observations traceable. Employer-stated salary and calculated comparison salary
are distinct concepts: annualization/comparability is DERIVED even if exposed next
to a preferred compensation view. Structure, normalization, currency conversion and
physical representation remain **DEFERRED**; unknown must not become zero.

A Job may expose one preferred application link selected from preserved link
roles/evidence. Multiple valid destinations may exist. Preferred-link changes do
not change identity. No physical Link table/entity is required; exact selection
and reliability algorithms remain **DEFERRED**.

No universal provider precedence is selected for all facts. Deadline selection
follows the accepted policy principles in section 8.2; exact field/provider rules
remain deferred without discarding the observations.

## 7. Provenance and Source Metadata

**TARGET:** retain enough source context to explain identity and factual selection,
including after duplicate consolidation:

| Concept | Responsibility |
|---|---|
| source | Collection origin/provider, independently of employer ATS. |
| source_job_id | Posting identifier and namespace, if observed; unknown is allowed. |
| source_url | Observed source listing/record locator, including identity-bearing parameters. |
| observed_at | Time of the actual source observation, not a later export or replay. |
| source-specific title | Wording that may differ from the selected canonical title. |
| source-specific employer | Original employer wording where it differs from Phase 1 normalized text. |
| compensation observations | Employer/source-stated amounts, wording, currency and period when observed; origin of any preferred compensation view. |
| explicit work terms | Remote/hybrid/on-site wording, geographic restrictions, attendance requirements and supporting evidence; distinct from normalized derived classification. |
| application/source link evidence | Preserve source locators and distinct direct-application link roles, including multiple destinations and evidence used by a preferred projection. |
| source-specific location | Original geography/work terms, including restrictions and ambiguous wording. |
| source-specific deadline | Observed cutoff wording/value, precision and origin, with subsequent changes retained. |
| raw or normalized source values | Evidence needed to explain transformations, such as original posting text, compensation/currency/interval, JD completeness, work terms and application links. |

Normalization should remain distinguishable from what the source explicitly said.
For example, a calculated date from “3 days ago” is not an exact observed posting
instant. Provenance need not preserve every payload forever; payload retention and
formats are **DEFERRED**, but discarded payload must not be mistaken for retained
evidence. A source URL alone cannot reconstruct a removed or changed JD/deadline.

**CURRENT:** `duplicate_urls` retains alternate locators but not a complete record
of source-specific facts or observations (`_merge_duplicate_job`). Source snapshot
`scraped_at` describes a save operation; zero-data paths can resave previous jobs
(`_scrape_jobspy_board`, `save_jobs_output`). It must not be blindly imported as
every job's actual `observed_at`.

## 8. Time Semantics

### 8.1 posted_at

**TARGET:** the employer- or source-stated posting date/time when available. Preserve
whether it is an exact date-time, date-only value, or interpretation of relative
wording; do not fabricate timezone or precision. Exact representation and preferred
source selection are **DEFERRED**. System discovery is a separate clock.

**CURRENT:** `date_posted` accepts source-varying strings; `_posted_text_to_iso`
converts relative Google text using the current UTC date and approximate week/month
lengths. `triage.html`, `jobFreshMs`, prefers `first_seen` for freshness. These
functions demonstrate why posting and discovery concepts must remain distinguishable.

### 8.2 application_deadline

**TARGET:** the employer-stated date or date-time after which applications for the
job are no longer expected to be accepted. Explicit source-reported employer
cutoffs are factual observations; an inferred urgency score is not a deadline.

Missing deadline information is unknown/null. It must not be interpreted as rolling
recruitment, indefinite availability or closure. A passed cutoff can inform later
verification or ranking policy but is not itself an implemented verifier.

Deadline observations may change: an employer can extend or correct a cutoff.
Preserve the observed values, origins and observation times rather than overwriting
the only evidence. Date-only information must stay date-only unless a timezone/time
is supported; `closing_date`'s current slicing is not a target precision guarantee.
Evidence for the current field: `_parse_csucareers_listing`.

**TARGET accepted policy:** preserve every trusted deadline observation with its
source and observation time. A preferred current deadline may be exposed, backed
by temporal observations rather than a scalar that loses changes/conflicts. This
requires no separate Deadline entity or physical storage design.

Selection should prefer stronger/authoritative employer or ATS evidence over
weaker aggregator evidence. Among comparable-authority evidence, a more recent
verified observation is generally preferred. “Verified observation” here means
evidence supporting the observed deadline; it is not interchangeable with a LIVE
assessment or an export timestamp. Source observation alone does not guarantee
such verification.

Conflicts must remain observable. Unresolved material conflict must not be silently
represented as a confidently established deadline; missing information and
conflicting known observations are different states. These accepted principles do
not guarantee that every disagreement can already be resolved algorithmically.
Exact precedence rules, verification/reliability algorithms and provider-specific
authority ranking remain **DEFERRED**. No provider-ranking table or numeric trust
score is defined.

Deadline urgency, days remaining and Daily Priority belong to derived application
intelligence. They must not replace or modify the employer-stated cutoff.

### 8.3 first_seen_at

**TARGET accepted semantics:** the earliest accepted actual source-observation time
associated with the canonical opening, rather than the time a canonical identifier
was assigned. If accepted earlier evidence is linked later, the value may move
earlier; combining equivalent records uses their accepted observation history.
The canonical identity remains stable.

An employer posting date is not earlier system discovery evidence. A legacy record
with only insertion `first_seen` does not prove an earlier upstream observation.
Importing imperfect history and handling merge/split corrections are **DEFERRED**;
preserve what is known rather than inventing observation history.

**CURRENT:** `_merge_into_all_jobs` stamps newly inserted copies with current UTC
`first_seen`, preserves existing values, and prunes on a lexical 30-day cutoff.
It does not adopt the earliest-source-observation semantics above. This design
does not change retention or reinterpret stored compatibility timestamps.

### 8.4 last_seen_at

**TARGET:** the latest accepted actual source-observation time associated with the
opening. Replaying cached records, saving exports or reusing a previous snapshot
must not advance it without a new observation. It records observation, not proof
of accepting applications: aggregators can still advertise closed jobs.

When both observation times are known, `first_seen_at <= last_seen_at`. A newly
observed opening may have equal times. Posting time and deadline need not have any
fixed order relative to discovery: backfills and late discovery are possible.
Verification has its own check time; no LIVE guarantee follows from `last_seen_at`.
**CURRENT:** no last-observation update exists in `_merge_into_all_jobs`.

## 9. Unknown and Nullable Semantics

**TARGET rule:** unknown remains unknown unless sufficient evidence supports a
stronger state. A nullable concept does not by itself explain why data is missing;
source evidence or processing context should preserve a distinction when useful.
No universal null taxonomy is proposed.

| Example | Required semantic distinction |
|---|---|
| Remote/work terms | Missing data is unknown. Explicit non-remote wording is different from a parser default. Generic remote wording does not establish cross-border eligibility. |
| Deadline | Unknown differs from explicitly stated rolling recruitment; neither is inferred from an empty field. Conflicting known observations differ from no observations. |
| Salary | Unknown differs from explicitly unpaid or an observed compensation statement. Do not turn missing bounds into zero. |
| ATS identity | Unknown provider/ID differs from evidence that the employer uses another application mechanism; a collection source is not a substitute. |
| Location | Unknown differs from explicitly unrestricted geography or a multi-location posting. Empty location does not remove eligibility restrictions. |
| Sponsorship/eligibility inputs | An explicit employer “no sponsorship” statement is evidence; missing sponsorship information is unknown. Candidate eligibility is a separate analysis, not an unknown boolean coerced to false. |

“Not yet observed” can describe a fact awaiting collection; “unknown” can describe
an unresolved value after collection. “Not applicable” requires positive contextual
evidence; “explicitly false” requires supported negative evidence. Represent these
separately only where downstream decisions materially depend on the distinction.
Exact encoding is **DEFERRED**. **CURRENT:** source strings, omission, `None` and
fallback values coexist (`_coerce_bool`, `_ingest_jobspy_df`, schema properties);
this design does not claim the rule is already enforced.

## 10. Derived Data Outside Canonical Job

**TARGET boundaries:** these may reference the Job, but are not its core facts or
identity. This section does not design their implementations.

| Information | Why outside core factual Job |
|---|---|
| Normalized role classification | DERIVED interpretation of title/JD, associated with/referenced from Job as a separate result/view. Taxonomy, versioning and persistence belong to Phase 2; never factual identity. |
| Seniority classification | Inference or normalized interpretation; retain explicit employer wording as evidence. |
| Derived work arrangement | Separate DERIVED normalization of provenance-owned explicit work wording/evidence. Exact taxonomy/representation is deferred; no unrestricted-geography or candidate-eligibility inference follows from remote wording. |
| Eligibility | Depends on candidate circumstances and deterministic policies; employer requirements can be facts without making the eligibility result a fact. |
| Fit Score | Candidate-specific role-fit assessment, intended to be relatively stable; not opening identity. |
| Daily Priority | Time- and action-dependent urgency/ranking, distinct from Fit Score and the factual deadline. |
| Skill extraction / skill gaps | Extraction applies a taxonomy/analysis; gaps additionally compare a candidate. JD wording remains source evidence. |
| Interview preparation | Generated/personal preparation material rather than employer-stated job data. |
| Application status | Candidate workflow action, not opening availability. Applied does not mean CLOSED. |
| User notes | Personal annotations, even when attached to a Job; not automatically verified employer facts. |
| Shortlist state | A user's selection or ranking decision, not identity or employer data. |
| Notion workflow state | Integration/human workflow representation. Ownership and synchronization direction remain unresolved. |

**CURRENT examples:** dashboard `_role`, `_sen`, `_work`, `_fit`, URL-keyed
`state.triage`/notes/stars, and legacy `scores.json` are separate or derived consumer
data (`triage.html`, `enrich`, `save`; `triage_agent.py`, `main`). Arbitrary
downstream fields on existing master records can survive merge
(`_merge_duplicate_job`; field-preservation tests). Preserving those compatibility
fields does not promote them into canonical facts.

## 11. Design Invariants

All rows are **TARGET accepted rules**, not assertions of current enforcement. Future
checks should exercise semantic boundaries rather than mirror implementation.

| Invariant | Suitable future enforcement |
|---|---|
| One canonical Job represents one real-world opening, not a URL or hiring seat. | Design-only meaning plus unit/contract and integration examples of equivalent/distinct openings; no schema alone proves real-world equivalence. |
| One source record maps to at most one Job at one time; multiple records may map to one Job. | Relationship/schema constraints when a representation is chosen; integration checks for mapping and correction. |
| Canonicalization preserves source provenance and selected-fact origin. | Contract/integration checks across normalization and merge; schema validation for required evidence links. |
| `source_url` and `direct_url` remain distinct semantic concepts, even when equal. | Schema descriptions and serializer/collector contract tests. |
| Unknown must not silently become false, CLOSED, zero salary or rolling recruitment. | Nullable schema constraints plus normalization/consumer contract tests; negative-evidence examples. |
| `first_seen_at <= last_seen_at` when both exist; replay/export does not count as fresh observation. | Schema or validation constraint plus clock-controlled unit/integration tests. |
| Posting, observation, verification and application-cutoff times are distinct. | Collector/serializer contract tests including relative dates, date-only precision, backfills and cached snapshots. |
| A deadline represents observed employer cutoff information; changing it preserves evidence. | Schema semantics plus deadline normalization/update integration tests. Accepted authority/recency and conflict-visibility principles require future contract tests; exact precedence remains deferred. |
| Candidate analysis and workflow state never participate in Job identity. | Identity contract tests showing that score, candidate, note or status changes leave identity unchanged. |
| Fuzzy title similarity alone cannot establish canonical equivalence. | Unit/contract tests for generic same-title distinct openings. Contract/integration tests should exercise accepted AUTO_MERGE / REVIEW / KEEP_SEPARATE tiers and contradiction blocking; numeric thresholds remain deferred. |
| Preferred compensation/link projections stay traceable to provenance; annualized/comparable salary stays derived and link changes do not affect identity. | Serializer and update contract/integration tests for evidence linkage, unknown compensation and multiple destinations. |
| Phase 1 employer representation is normalized text; role/work classifications stay separate from factual core. | Model/normalization contract tests retaining original employer/work wording and stable identity across reclassification. |
| Scoped source/ATS IDs are not interchangeable with canonical ID or unqualified numeric tokens. | Namespace/identity contract tests; schema constraints after representation decisions. |
| Mutable title, deadline, preferred URL or classification changes do not alone replace canonical identity. | Update and compatibility integration tests; merge/split correction policy remains deferred. |
| Compatibility projection does not silently replace existing URL/state or timestamp semantics. | Golden/contract and consumer integration tests for existing envelopes, aliases and URL-keyed attachments. |

No tests or executable constraints are added by this document. The existing tests
in section 3 establish current behaviour only.

## 12. Compatibility With Existing JSON Outputs

**TARGET boundary:**

```text
Canonical domain representation
        ↓
compatibility transformation / serializer
        ↓
existing JSON outputs and consumers
```

The internal domain need not adopt current field names or envelopes. Compatibility
must be explicit: a new canonical ID, actual ATS concept, or observation timestamp
must not silently replace a legacy URL key, source `ats` label, or `first_seen`.

| CURRENT surface | Evidence and compatibility expectation |
|---|---|
| `output/all_jobs.json`: `{updated_at,jobs}` | `_merge_into_all_jobs`; dashboard, legacy agent and weekly digest read `jobs`. Preserve the envelope, filenames, UTC display metadata and legacy discovery/retention behaviour until explicit validated change. |
| Normal source snapshots: `{scraped_at,total,new_count,jobs,new_jobs}` | `save_jobs_output` overwrites each snapshot. Source newness is previous-source-snapshot identity, not first canonical discovery. Preserve this distinction for digests/notifications. |
| Legacy default `jobs.json`: `{scraped_at,total,jobs}` | `save_results` is the retained persistence exception without master merge/instant notification. Do not assume all envelopes have newness fields. |
| Record fields and extensions | Schema and `_merge_duplicate_job`: existing `url`, `ats`, `date_posted`, `first_seen`, salary/description/work fields, `duplicate_urls` and surviving downstream extensions matter. An export adapter must define aliases/unknown conversions rather than silently reinterpret them. |
| Dashboard source union and annotations | `SOURCES`, `loadJobs`, `enrich`, `save`: fixed filenames; source records win exact URLs, master backfills missing `first_seen`; optional scores and `jobTriage:v3` annotations use raw URL keys. Canonical IDs do not migrate browser keys automatically. |
| Notifications | `save_jobs_output` passes source-new jobs to `notify_new_jobs`; `_identity` tracks normalized company/title in `notified.json`. Weekly `_recent_jobs` selects master `first_seen`; `_score_job` reads URL-keyed scores. Avoid silently changing newness, tracker or time selection. |
| Legacy AI | `triage_agent.py`, `load_jobs`, `main`: master default, selected source fallback, raw-URL score map, error verdict retry, discovery cutoff and pruning. New identities require explicit attachment/alias handling rather than abandoning scores. |
| CLI/config/workflows | `scrape_jobs.py` dispatch and `_load_config`; [linkedin_watch.yml](../../.github/workflows/linkedin_watch.yml), [triage.yml](../../.github/workflows/triage.yml), [weekly_digest.yml](../../.github/workflows/weekly_digest.yml): source/backfill flags, configuration names, invocation and output paths remain contracts. No change is authorized here. |

The schema/output discrepancies in section 3 mean “preserve compatibility” cannot
mean “all current records already conform to the schema.” A future contract must
identify the relevant producer/consumer behaviour and deliberately validate any
schema correction. Unknown facts should remain unknown in the domain; legacy
projection choices must be explicit and must not invent facts. Likewise, target
`first_seen_at` is not an automatic rename of current `first_seen`; mapping
historical timestamps needs a later validated compatibility decision.

**Accepted storage direction**, owned by
[ARCHITECTURE.md](../../ARCHITECTURE.md#intended-storage-authority-transition):
existing JSON primary path → temporary Postgres shadow write → storage parity
validation → explicit Postgres cutover → Postgres as system of record → JSON as
generated compatibility/export artifacts. Permanent JSON/Postgres dual-write is
not the target. **CURRENT:** JSON remains the implemented persistence path
(`save_jobs_output`, `_merge_into_all_jobs`). This document defines neither shadow
writing nor parity/cutover/recovery implementation.

## 13. Alternatives Considered

### A. One large Job object containing everything

A single object can simplify transport and initially resemble permissive current
JSON. However, facts, observations, candidate assessments and workflow have
different lifetimes and authorities. It couples scoring/status changes to factual
updates and makes provenance hard to distinguish. **Accepted choice:** separate
domain responsibilities; a composed read view may still be convenient without
making every included value a canonical fact.

### B. Treat every source record as a canonical Job

This makes ingestion simple and preserves source detail. It fails to represent one
opening advertised across boards, retaining duplication in downstream analysis and
workflow. **CURRENT motivation:** master and browser already attempt cross-record
consolidation (`_same_job`, `dedupe`). **Accepted choice:** source records remain
distinct evidence associated with canonical openings.

### C. Use URL as canonical Job identity

URLs are immediately available, clickable and compatible with current state/scores.
They vary by tracking, board, redirect and reposting; generic URLs can also hide
material query IDs. **CURRENT evidence:** `_job_identity`, `duplicate_urls`, Google
apply-link selection and URL-keyed scores. **Accepted choice:** URL remains
locator/identity evidence and a compatibility key, not the definition of an opening.

### D. Make the current JSON schema the permanent domain model

It preserves familiar names and supplies existing fixture validation. But it
declares URL as primary key, mixes collection source with ATS, requires a timestamp
not added to snapshots, excludes null remote values produced by normalizers, and
allows arbitrary consumer fields. It does not express provenance/history or shared
canonical identity. **Accepted choice:** preserve and explicitly adapt current
JSON contracts while designing a separate domain contract. No schema replacement
or output redesign is performed here.

## 14. Deferred Decisions

Semantic ownership and the evidence-tier/deadline policy principles are accepted.
The items below defer implementation representation or detailed evaluation, not
those decisions. Each must be addressed by its owning design/ExecPlan before the
relevant implementation; none authorizes an implicit default.

| Decision | Why it can wait at this boundary |
|---|---|
| Physical Postgres schema | Accepted semantics can be implemented/evaluated independently of tables, types, indexes or ORM; persistence design must precede database work. |
| Canonical ID generation and merge/split correction | Stable opening identity and evidence tiers are accepted; concrete IDs and correction/recovery mechanics require bounded implementation/lifecycle design. |
| Exact ATS/source identity evaluation and numeric similarity thresholds | Scoped identities, evidence tiers and contradiction safeguards are accepted. Provider extraction/identifier reuse, group validation and numeric evaluation require fixtures/real data; probable similarity cannot silently become AUTO_MERGE. |
| Provider-specific deadline precedence and evidence verification | Authority/recency principles and observable uncertainty are accepted. Exact ranking/reliability rules require source-specific evidence; no hard ranking or trust scores are assumed. |
| Exact salary representation, normalization and currency conversion | Source compensation ownership, allowed traceable preferred canonical view and DERIVED comparison values are settled; formats/algorithms need separate validation without inventing missing values. |
| Preferred-link selection/reliability algorithms | Link evidence ownership and a non-identifying preferred Job projection are settled; multiple destinations remain preserved while selection rules are evaluated. |
| Company identity beyond Phase 1 | Phase 1 uses normalized employer text with source wording retained. Alias resolution, legal entities, parent/subsidiary relationships and a separate canonical Company model can be designed later. |
| Exact location normalization | Preserve location/restriction wording while evaluating a representation; no new Location entity is required here. |
| Exact work-arrangement taxonomy/representation | Explicit work evidence is provenance and normalized work arrangement is separate DERIVED classification. Enum names and algorithms can be chosen later without reopening ownership. |
| Role taxonomy, versioning and persistence | Separate derived role results/views may reference Job; detailed representation belongs to Phase 2 and does not affect factual identity. |
| JSON envelope redesign and historical field mapping | Existing compatibility remains required; any format or target/legacy timestamp conversion needs an explicitly validated change. |
| Postgres/Notion ownership and synchronization direction | Canonical facts and human workflow are distinguishable without assigning write permissions or bidirectional rules. Phase 2 design must decide them explicitly. |
| Live verifier implementation | Three-state semantics remain separate; provider rules, assessment freshness/aggregation and scheduling need later design. |
| Migration, parity and recovery mechanics | Architecture owns the accepted authority transition; operational delivery belongs to later designs/ExecPlans. |
| Raw-payload retention and executable contract format/location | Provenance semantics do not require keeping every payload forever or choosing a machine-readable format here. The first bounded implementation plan must select its executable acceptance contract. |

These deferrals do not block acceptance of the semantic foundation. The next
planning task must bound implementation and settle the representation decisions
needed for that scope; acceptance does not authorize guessing them during coding.

## 15. Resolved Design Decisions

The user approved the seven review resolutions on 2026-09-15. All former material
semantic questions are resolved for the first canonical Job foundation milestone.
The owning sections below contain their contracts; no additional blocking semantic
question is introduced.

| Former question | Accepted disposition / owning section |
|---|---|
| 1. Salary ownership | Provenance owns compensation observations; a traceable preferred canonical view is allowed, with comparison salary DERIVED. Section 6. |
| 2. Work arrangement | Explicit work wording/evidence is provenance; normalized classification is separate DERIVED data. Sections 4.5, 6 and 10. |
| 3. Application link | Preserved link/provenance evidence supplies an optional preferred application projection; it is not identity and requires no physical Link entity. Sections 6–7. |
| 4. Deadline conflict | Preserve trusted observations; prefer stronger authority and generally newer verified comparable-authority evidence, while keeping conflict/uncertainty observable. Section 8.2. |
| 5. Company identity | Normalized employer text in Phase 1, source wording retained; no separate Company entity in Phase 1. Section 6. |
| 6. Role classification | Separate DERIVED result/view may reference Job; taxonomy/versioning/persistence belong to Phase 2 and cannot change identity. Sections 4.5 and 10. |
| 7. Merge evidence | `AUTO_MERGE`, `POSSIBLE_MATCH / REVIEW`, `KEEP_SEPARATE` tiers; material contradiction blocks automatic equivalence despite similarity. Section 5.4. |

Implementation-level deferrals are recorded in section 14. Notion ownership and
synchronization remain future Phase 2 decisions, not hidden resolutions here.

## 16. Design Acceptance Criteria

The design satisfies the semantic acceptance criteria below after the approved
review resolutions. Checked items describe the document, not executable conformance
or delivered capabilities:

- [x] CURRENT claims name inspected code/schema/tests/data; TARGET semantics are
  distinguishable from implemented reality.
- [x] One Job means one real-world opening; canonical, source and ATS identity are
  distinguishable, without a concrete hash or fuzzy-title-only identity rule.
- [x] Factual Job data and source/provenance have separate responsibilities;
  canonicalization preserves observations rather than just alternate URLs.
- [x] Verification is a separate assessment with `LIVE / CLOSED / UNKNOWN` meaning;
  observation does not imply LIVE.
- [x] Derived classification and candidate-specific analysis/workflow are outside
  core factual identity; their accepted associations and deferred representation
  are visible.
- [x] Posting, application deadline, first observation and last observation have
  explicit separate meanings and ordering constraints.
- [x] `application_deadline` is an observed employer cutoff; missing means unknown,
  changes retain provenance, accepted conflict principles preserve uncertainty and
  urgency remains derived.
- [x] Unknown is not silently negative, zero, unrestricted, CLOSED or rolling;
  exact encodings remain deferred where appropriate.
- [x] Compatibility transformation addresses current envelopes, source newness,
  raw URL attachments, timestamp meanings, CLI/config/workflow surfaces and drift.
- [x] Important invariants identify future executable verification without adding
  tests or claiming current enforcement.
- [x] Physical database design, migration/parity/recovery, Notion ownership and
  synchronization, and implementation sequencing remain deferred.
- [x] All seven material semantic decisions are resolved through user approval;
  section 14 separates accepted ownership from deferred implementation details.

Status moved from Proposed to Accepted through the user-approved review resolution.
No material semantic blocker remains for planning the first foundation milestone.
Accepted does not mean implemented: code, schema and tests must later establish
executable conformance. A future bounded ExecPlan owns implementation scope and
its acceptance contract. The
[point-in-time audit](../references/current-repository-audit.md) remains historical
inspection evidence; [current-state.md](../current-state.md) owns only the handoff.
