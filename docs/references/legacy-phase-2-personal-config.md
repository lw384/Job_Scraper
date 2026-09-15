> **Historical reference — earlier configuration milestone.** The Phase 2 name
> below uses the earlier customization numbering, not Application Intelligence
> Phase 2. This document does not govern [the current roadmap](../ROADMAP.md).
> Re-verify runtime claims; use [the catalog](../README.md) for current context.

# Phase 2 — Ivy / Wei Personal Search Configuration

Phase 2 moves the active search from the neutral template to a configuration-led,
UK-primary job-discovery scope. It deliberately does not add role enrichment,
remote-eligibility inference, experience extraction, or scoring algorithms.

## Canonical search intent

`config.json` is the source of truth for:

- Target role families and the complete primary title list
- UK-primary geography and a separate international-remote discovery bucket
- Existing strengths, AI-transition strengths, and development opportunities
- Off-target domains that should later be deprioritized, not substring-filtered

The source-specific `search_terms` and `locations` lists are bounded execution
subsets. They can change for rate limits or board coverage without changing the
canonical career definition in `search_scope`.

## Discovery boundaries

The location allow-list is configuration-driven. UK cities and configured remote
signals are retained; US states no longer bypass the config automatically.

Remote is only a discovery signal in this phase. For example, `Remote — US only`
is retained so a later phase can classify it as region-restricted. Phase 2 does
not create or infer `remote_geo_eligibility` or `China Eligible`.

Negative domains and development opportunities are also non-filtering metadata.
`keywords.exclude` remains empty, which prevents titles such as “Software Engineer
building analytics tools” from being dropped because of adjacent vocabulary.

## Active query budget

| Source | Phase 2 execution plan |
|---|---|
| LinkedIn | 11 terms × 2 locations = 22 combinations |
| Indeed | 8 terms × 5 UK locations = 40 combinations |
| Glassdoor | 8 terms × 2 UK locations = 16 combinations; workflow remains opt-in |
| Google Jobs | 14 paired UK/remote queries with explicit fallback locales |
| ZipRecruiter | Inactive until UK support is verified |
| HiringCafe | Inactive because the current implementation uses its US SEO route |
| Legacy US public-sector sources | Manual-only workflows with empty search terms |

The personal config is tracked because scheduled Actions and GitHub Pages both read
it from the checkout. It contains no credentials or private CV text; those remain
in GitHub Secrets or ignored personal files.

Google's exact-query entries carry `location` and `country` only so optional API
fallbacks do not silently execute from a US default. This locale context changes
search execution, not the later remote-work eligibility decision.
