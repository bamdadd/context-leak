"""CLI scenario-selection tests: --list-scenarios and --scenario <id>."""

from __future__ import annotations

import pytest

from context_leak.cli import main
from context_leak.scenarios import ALL_SCENARIOS


def test_list_scenarios_prints_ids_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--list-scenarios"])
    assert rc == 0
    printed = capsys.readouterr().out.split()
    assert printed == [scenario.id for scenario in ALL_SCENARIOS]


def test_scenario_by_id_runs(capsys: pytest.CaptureFixture[str]) -> None:
    scenario_id = ALL_SCENARIOS[0].id
    rc = main(["--scenario", scenario_id])
    assert rc == 0
    assert f"scenario={scenario_id}" in capsys.readouterr().out


def test_unknown_scenario_exits_nonzero_with_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--scenario", "no-such-scenario"])
    assert exc_info.value.code != 0
    err = capsys.readouterr().err
    assert "unknown scenario 'no-such-scenario'" in err
    assert "--list-scenarios" in err


def test_default_scenario_unchanged(capsys: pytest.CaptureFixture[str]) -> None:
    # No --scenario runs the club-reserve scenario as before.
    rc = main([])
    assert rc == 0
    assert "scenario=club-reserve-quarterly" in capsys.readouterr().out
