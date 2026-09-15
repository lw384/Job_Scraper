"""Regression tests for the configuration-driven discovery location filter."""

import pytest

import scrape_jobs
from scrape_jobs import is_target_location


US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]

DISCOVERY_TERMS = [
    "united kingdom", "uk", "england", "scotland", "london", "birmingham",
    "coventry", "manchester", "cambridge", "oxford", "bristol", "edinburgh",
    "leeds", "reading", "remote", "worldwide", "global", "anywhere",
    "apac", "asia", "china",
]


@pytest.fixture(autouse=True)
def _phase2_locations(monkeypatch):
    monkeypatch.setattr(scrape_jobs, "TARGET_LOCATIONS", DISCOVERY_TERMS)


@pytest.mark.parametrize("state", US_STATES)
def test_us_states_are_not_implicitly_accepted(state):
    """Legacy US state names must not bypass the configured allow-list."""
    assert is_target_location(f"City, {state}, United States") is False


@pytest.mark.parametrize(
    "location",
    [
        "London, England, United Kingdom",
        "Birmingham, England, United Kingdom",
        "Coventry, UK",
        "Greater Manchester, England",
        "Cambridge, England",
        "Oxford, England",
        "Bristol, England",
        "Edinburgh, Scotland",
        "Leeds, England",
        "Reading, England",
    ],
)
def test_uk_primary_locations_are_accepted(location):
    assert is_target_location(location) is True


@pytest.mark.parametrize(
    "location",
    [
        "Remote",
        "Remote — US only",
        "Worldwide remote",
        "Global",
        "Work from anywhere",
        "Remote, APAC",
        "Asia Pacific",
        "Shanghai, China",
    ],
)
def test_remote_discovery_signals_are_retained(location):
    """Retention for discovery does not assert China eligibility."""
    assert is_target_location(location) is True


@pytest.mark.parametrize(
    "location",
    [
        "Toronto, Canada",
        "Paris, France",
        "Berlin, Germany",
        "Tokyo, Japan",
        "New York, United States",
        "Sydney, Australia",
        "Phuket, Thailand",
    ],
)
def test_non_target_onsite_locations_are_rejected(location):
    assert is_target_location(location) is False


def test_short_uk_term_uses_word_boundaries():
    assert is_target_location("Phuket, Thailand") is False
    assert is_target_location("Remote, UK") is True


def test_empty():
    assert is_target_location("") is False


def test_none():
    assert is_target_location(None) is False  # type: ignore[arg-type]
