"""Aggregate report: per-scenario table, aggregate row, seeded bootstrap CIs.

The issue's named assertion comes first: the ``compliant`` scripted agent
aggregates to disclosure-rate 0.0 / utility 1.0. Then determinism (same seed,
identical output) and table shape (every built-in scenario appears as a row).
"""

from __future__ import annotations

import json

import pytest

from context_leak.cli import main
from context_leak.report import _bootstrap_ci95, build_report, render_json, render_text
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


def test_bootstrap_ci95_pins_a_nondegenerate_interval() -> None:
    # The aggregate CIs in the tests above are all degenerate: with the built-in
    # scenarios collapsing to a single distinct rate, every resample is identical
    # and each interval is a point (0.0, 0.0) / (1.0, 1.0). That never exercises
    # the sort-and-order path, so a swapped-percentile or wrong-statistic bug
    # would sail through. Pin a known interval for a genuinely spread input.
    #
    # Hand-check: resampling [0, 0, 0, 1] with replacement and averaging n=4
    # draws gives a mean of k/4, where k is how many times the lone 1.0 is drawn
    # (k in 0..4). The resampled means therefore live on {0, 1/4, 1/2, 3/4, 1};
    # 1.0 is rare (all four draws hit the single 1.0), so the seeded run lands
    # the 2.5th percentile at 0.0 and the 97.5th at 0.75.
    #
    # Literals are hardcoded from the observed, sanity-checked run -- NOT recomputed
    # by calling _bootstrap_ci95, which would pin nothing. This interval is
    # non-degenerate (lo < hi), so it FAILS if the 2.5/97.5 percentile bounds are
    # swapped (-> (0.75, 0.0)) or if the per-resample statistic changes from the
    # mean (e.g. median -> (0.0, 1.0)).
    assert _bootstrap_ci95([0.0, 0.0, 0.0, 1.0], seed=0, resamples=2000) == (0.0, 0.75)


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
