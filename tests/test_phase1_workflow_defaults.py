"""Regression tests for the Phase 1 automation boundary."""

from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"


def _workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "name",
    [
        "scrape_jobs.yml",
        "usajobs_watch.yml",
        "calcareers_watch.yml",
        "csucareers_watch.yml",
        "localgov_watch.yml",
        "triage.yml",
        "evals.yml",
    ],
)
def test_legacy_or_ai_workflows_are_manual_only(name):
    workflow = _workflow(name)

    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow


@pytest.mark.parametrize(
    "name",
    [
        "linkedin_watch.yml",
        "indeed_watch.yml",
        "glassdoor_watch.yml",
        "ziprecruiter_watch.yml",
        "google_jobs_watch.yml",
        "hiringcafe_watch.yml",
    ],
)
def test_active_general_board_workflows_remain_scheduled(name):
    assert "schedule:" in _workflow(name)


def test_priority_workflow_uses_supported_cli_flag():
    workflow = _workflow("scrape_jobs.yml")

    assert "--priority-only" in workflow
    assert "--biotech-only" not in workflow


def test_evals_no_longer_run_on_push():
    assert "push:" not in _workflow("evals.yml")


def test_watchdog_only_rescues_active_general_board_workflows():
    workflow = _workflow("linkedin_watch_backup.yml")

    assert "workflow run linkedin_watch.yml" in workflow
    assert "workflow run indeed_watch.yml" in workflow
    assert "workflow run scrape_jobs.yml" not in workflow


def test_setup_does_not_dispatch_legacy_or_ai_workflows():
    setup = (ROOT / "scripts" / "setup.sh").read_text(encoding="utf-8")

    for name in (
        "scrape_jobs.yml",
        "usajobs_watch.yml",
        "calcareers_watch.yml",
        "csucareers_watch.yml",
        "localgov_watch.yml",
        "triage.yml",
        "evals.yml",
    ):
        assert f'["{name}"]' not in setup
        assert f'workflow run "{name}"' not in setup
    assert "gh secret set ANTHROPIC_API_KEY" not in setup


@pytest.mark.parametrize(
    "name",
    [
        "scrape_jobs.yml",
        "usajobs_watch.yml",
        "calcareers_watch.yml",
        "csucareers_watch.yml",
        "localgov_watch.yml",
        "triage.yml",
    ],
)
def test_manual_data_writers_keep_commit_serialization(name):
    assert "group: job-scraper-commit-push" in _workflow(name)
