"""Regression tests for the domain-neutral Phase 1 defaults."""

import json
from pathlib import Path

import notify
import scrape_jobs


ROOT = Path(__file__).parent.parent


def _load_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_example_search_configuration_is_domain_neutral():
    config = _load_json("config.example.json")

    assert config["search_scope"]["role_families"] == []
    assert config["search_scope"]["primary_search_terms"] == []
    assert config["search_scope"]["geography"]["uk_primary"] == []
    assert config["search_scope"]["geography"]["international_remote_discovery"] == []
    assert config["skills"]["existing_strengths"] == []
    assert config["skills"]["ai_transition_strengths"] == []
    assert config["skills"]["development_opportunities"] == []
    assert config["negative_domains"]["terms"] == []
    assert all(not value for key, value in config["search_terms"].items()
               if not key.startswith("_"))
    assert all(not value for key, value in config["locations"].items()
               if not key.startswith("_") and key != "linkedin_partitions")
    assert config["locations"]["linkedin_partitions"]["states"] == []
    assert config["locations"]["linkedin_partitions"]["high_volume"]["locations"] == []
    assert config["location_filter"]["terms"] == []
    assert config["keywords"]["include"] == []
    assert config["keywords"]["exclude"] == []
    assert config["employers"]["priority"] == []
    assert config["employers"]["exclude"] == []
    assert config["priority_topics"]["terms"] == []
    assert config["role_categories"]["terms"] == []


def test_example_scoring_profile_has_no_domain_rules():
    profile = _load_json("scoring_profile.example.json")

    assert profile["fit_terms"] == []
    assert profile["signature_terms"] == []
    assert profile["poor_fit_terms"] == []
    assert profile["calibration_cases"] == []


def test_empty_keyword_configuration_is_fail_closed():
    assert scrape_jobs._build_title_re([]).search("any job title") is None
    assert scrape_jobs.title_matches_keywords("Environmental Scientist") is False


def test_empty_scoring_profile_assigns_zero_fit(monkeypatch):
    monkeypatch.setattr(notify, "_SCORING_PROFILE", None)
    assert notify._fit("Any job title", "Any description") == 0


def test_dashboard_fallbacks_are_domain_neutral():
    dashboard = (ROOT / "triage.html").read_text(encoding="utf-8")

    assert "<title>Job Discovery &amp; Triage</title>" in dashboard
    assert "let EXCLUDE_COMPANY = [];" in dashboard
    assert "let ROLE_CATS = [];" in dashboard
    assert "let FIT_TERMS = [];" in dashboard
    assert "let STAR_TERMS = [];" in dashboard
    assert "environmental protection agency" not in dashboard
    assert "microplastic|nanoplastic" not in dashboard
    assert "stantec|arcadis|ramboll" not in dashboard
