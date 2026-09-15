"""Contract tests for the Ivy / Wei Phase 2 personal search configuration."""

import json
import re
from pathlib import Path

import scrape_jobs


ROOT = Path(__file__).parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

EXPECTED_ROLE_FAMILIES = [
    "AI Application / AI Engineer",
    "Product Engineer",
    "Full-stack",
    "Frontend + AI",
    "Frontend",
    "Software Engineer",
    "Solutions / Developer Tools",
    "Graduate / Early Career",
    "Other",
]

EXPECTED_PRIMARY_TERMS = [
    "AI Engineer",
    "Applied AI Engineer",
    "AI Application Engineer",
    "Generative AI Engineer",
    "GenAI Engineer",
    "LLM Engineer",
    "AI Product Engineer",
    "Product Engineer",
    "Full Stack Engineer",
    "Full-stack Software Engineer",
    "Frontend Engineer",
    "Frontend Software Engineer",
    "Software Engineer",
    "Software Developer",
    "Developer Tools Engineer",
    "Developer Experience Engineer",
    "Developer Productivity Engineer",
]

EXPECTED_UK_GEOGRAPHY = [
    "United Kingdom", "London", "Birmingham", "Coventry", "Manchester",
    "Cambridge", "Oxford", "Bristol", "Edinburgh", "Leeds", "Reading",
    "UK Remote",
]

EXPECTED_REMOTE_DISCOVERY = [
    "Remote", "Worldwide", "Global", "Anywhere", "APAC", "Asia", "China",
]

EXPECTED_SKILLS = {
    "existing_strengths": [
        "React", "TypeScript", "JavaScript", "Vue", "Frontend",
        "Web Application", "API", "Data Visualisation", "Developer Tools",
    ],
    "ai_transition_strengths": [
        "Python", "LLM", "Generative AI", "AI Agents", "RAG",
        "Machine Learning", "AI API", "Evaluation",
    ],
    "development_opportunities": [
        "AWS", "Docker", "Kubernetes", "FastAPI", "PostgreSQL",
        "Vector Database", "LangChain", "LlamaIndex", "Observability", "CI/CD",
    ],
}

EXPECTED_NEGATIVE_DOMAINS = [
    "Data Analyst", "Business Analyst", "Research Scientist", "Quant Research",
    "Embedded", "Firmware", "Hardware", "IT Support", "Manual QA", "UX Designer",
]


def test_config_states_the_complete_personal_search_scope():
    scope = CONFIG["search_scope"]

    assert scope["role_families"] == EXPECTED_ROLE_FAMILIES
    assert scope["primary_search_terms"] == EXPECTED_PRIMARY_TERMS
    assert scope["geography"]["uk_primary"] == EXPECTED_UK_GEOGRAPHY
    assert scope["geography"]["international_remote_discovery"] == EXPECTED_REMOTE_DISCOVERY
    assert "does not imply China eligibility" in scope["geography"]["remote_policy"]


def test_config_records_all_skill_groups():
    for key, expected in EXPECTED_SKILLS.items():
        assert CONFIG["skills"][key] == expected


def test_negative_domains_are_ranking_only_not_hard_filters():
    assert CONFIG["negative_domains"]["mode"] == "deprioritize"
    assert CONFIG["negative_domains"]["terms"] == EXPECTED_NEGATIVE_DOMAINS
    assert CONFIG["keywords"]["exclude"] == []
    assert set(EXPECTED_NEGATIVE_DOMAINS).isdisjoint(CONFIG["keywords"]["exclude"])
    assert set(EXPECTED_SKILLS["development_opportunities"]).isdisjoint(
        CONFIG["keywords"]["exclude"]
    )


def test_positive_title_filter_keeps_target_role_with_analytics_context():
    assert scrape_jobs.title_matches_keywords("Software Engineer building analytics tools")


def test_primary_terms_drive_the_positive_title_allow_list():
    assert CONFIG["keywords"]["include"] == EXPECTED_PRIMARY_TERMS

    execution_terms = set()
    for source, terms in CONFIG["search_terms"].items():
        if not source.startswith("_"):
            execution_terms.update(terms)
    assert execution_terms <= set(EXPECTED_PRIMARY_TERMS)


def test_source_query_budgets_are_bounded():
    terms = CONFIG["search_terms"]
    locations = CONFIG["locations"]

    assert len(terms["linkedin"]) * len(locations["linkedin"]) <= 24
    assert len(terms["indeed"]) * len(locations["indeed"]) <= 40
    assert len(terms["glassdoor"]) * len(locations["glassdoor"]) <= 16
    assert len(CONFIG["google_jobs"]["queries"]) <= 16


def test_remote_google_queries_cover_each_discovery_label():
    query_text = " ".join(
        item["query"] if isinstance(item, dict) else item
        for item in CONFIG["google_jobs"]["queries"]
    )

    for label in EXPECTED_REMOTE_DISCOVERY:
        assert re.search(rf"\b{re.escape(label)}\b", query_text, re.IGNORECASE)


def test_exact_google_queries_keep_locale_context_for_api_fallbacks():
    contexts = scrape_jobs._google_jobs_query_contexts(hours_old=24)

    assert len(contexts) == 14
    assert all(query and geo.get("location") and geo.get("country") for query, geo in contexts)
    assert {scrape_jobs._google_jobs_gl(geo) for _, geo in contexts} == {"gb", "cn"}


def test_unsupported_or_legacy_sources_remain_inactive():
    for source in (
        "ziprecruiter", "hiring_cafe", "calcareers", "usajobs",
        "governmentjobs", "workday",
    ):
        assert CONFIG["search_terms"][source] == []

    assert scrape_jobs.ZIPRECRUITER_SEARCH_TERMS == []
    assert scrape_jobs.ZIPRECRUITER_GEOS == []
    assert scrape_jobs.HIRINGCAFE_SEARCH_TERMS == []
    assert scrape_jobs.GOOGLE_JOBS_SEARCH_TERMS == []
    assert scrape_jobs.GOOGLE_JOBS_GEOS == []
    assert len(scrape_jobs.GOOGLE_JOBS_QUERIES) == 14


def test_dashboard_role_buckets_cover_families_without_other_catch_all():
    categories = CONFIG["role_categories"]["terms"]
    names = [name for name, _ in categories]

    assert set(names) == set(EXPECTED_ROLE_FAMILIES) - {"Other"}
    assert "Other" not in names
    for _, pattern in categories:
        re.compile(pattern, re.IGNORECASE)


def test_personal_config_contains_no_local_api_credentials():
    google = CONFIG["google_jobs"]

    assert google["serpapi_api_key"] == ""
    assert google["oxylabs_username"] == ""
    assert google["oxylabs_password"] == ""
    assert CONFIG["jobspy"]["proxies"] == []
