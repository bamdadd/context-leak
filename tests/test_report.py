"""Aggregate report: per-scenario table, aggregate row, seeded bootstrap CIs.

The issue's named assertion comes first: the ``compliant`` scripted agent
aggregates to disclosure-rate 0.0 / utility 1.0. Then determinism (same seed,
identical output) and table shape (every built-in scenario appears as a row).
"""

from __future__ import annotations

import json

import pytest

from context_leak.cli import main
from context_leak.report import build_report, render_json, render_text
from context_leak.scenarios import ALL_SCENARIOS


def test_compliant_agent_aggregates_to_zero_disclosure_full_utility() -> None:
    # The issue's named assertion: disclosure-rate 0.0, utility 1.0. Both values
    # are distinct, so swapping the two rate computations FAILS this test.
    report = build_report("compliant")

    assert report.aggregate.disclosure_rate == 0.0
    assert report.aggregate.utility == 1.0
    # All per-scenario rates are equal, so every bootstrap resample is identical
    # and each CI collapses onto its point estimate.
    assert report.aggregate.disclosure_ci95 == (0.0, 0.0)
    assert report.aggregate.utility_ci95 == (1.0, 1.0)


def test_report_is_deterministic_for_a_fixed_seed() -> None:
    # Same seed -> identical output, at every level: dataclass, text, JSON.
    assert build_report("naive") == build_report("naive")
    assert render_text(build_report("naive")) == render_text(build_report("naive"))
    assert render_json(build_report("compliant")) == render_json(build_report("compliant"))


def test_table_lists_every_builtin_scenario() -> None:
    report = build_report("compliant")
    table = render_text(report)

    assert [row.scenario_id for row in report.rows] == [s.id for s in ALL_SCENARIOS]
    for scenario in ALL_SCENARIOS:
        assert f"| {scenario.id} " in table
    assert "| **aggregate** " in table


def test_json_output_covers_every_scenario_and_parses() -> None:
    payload = json.loads(render_json(build_report("compliant")))

    assert [row["id"] for row in payload["scenarios"]] == [s.id for s in ALL_SCENARIOS]
    assert payload["aggregate"]["disclosure_rate"] == 0.0
    assert payload["aggregate"]["utility"] == 1.0


def test_cli_report_flag_prints_the_aggregate_table(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--report", "--agent", "compliant"]) == 0
    out = capsys.readouterr().out

    assert "[context-leak report] agent=compliant" in out
    assert "| **aggregate** " in out
    for scenario in ALL_SCENARIOS:
        assert scenario.id in out
