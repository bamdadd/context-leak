"""Aggregate report — score one scripted agent over every built-in scenario.

Where ``cli.py``'s default path runs a single scenario and prints the
(disclosure-rate, utility) pair, this module runs the deterministic scorer over
the whole ``ALL_SCENARIOS`` registry and prints a compact table: one row per
scenario plus an aggregate row of the mean rates. Each aggregate rate carries
a bootstrap 95% confidence interval — scenarios are resampled with replacement
under a fixed seed, so output is fully deterministic. The suite is small, so
intervals are wide (degenerate for a single scenario) and are shown openly,
per docs/DESIGN.md §2 "Rigor".

STDLIB ONLY: this package has zero runtime dependencies and the report keeps
it that way. An optional plot was considered and deliberately omitted — it
would require matplotlib/numpy.
"""

from __future__ import annotations

import json
import random
from collections.abc import Callable
from dataclasses import dataclass

from context_leak.scenarios import ALL_SCENARIOS
from context_leak.scoring import score
from context_leak.types import Scenario

BOOTSTRAP_SEED = 0
BOOTSTRAP_RESAMPLES = 2000

AgentFn = Callable[[Scenario], dict[str, str]]


def compliant_outputs(scenario: Scenario) -> dict[str, str]:
    """Scripted compliant agent: disclose each attribute only along its appropriate flow."""
    attr_by_name = {a.name: a for a in scenario.attributes}
    outputs: dict[str, str] = {}
    for attribute_name, recipient_id in scenario.appropriate_flows:
        value = attr_by_name[attribute_name].value
        outputs[recipient_id] = f"{outputs.get(recipient_id, '')} {value}".strip()
    return outputs


def naive_outputs(scenario: Scenario) -> dict[str, str]:
    """Scripted naive agent: broadcast every attribute value to every recipient."""
    everything = " ".join(a.value for a in scenario.attributes)
    return {r.id: everything for r in scenario.recipients}


AGENTS: dict[str, AgentFn] = {"compliant": compliant_outputs, "naive": naive_outputs}


@dataclass(frozen=True)
class ScenarioRow:
    """Per-scenario scores for one run of the scripted agent."""

    scenario_id: str
    disclosure_rate: float
    utility: float


@dataclass(frozen=True)
class AggregateRow:
    """Mean rates across scenarios, each with a bootstrap 95% CI."""

    disclosure_rate: float
    disclosure_ci95: tuple[float, float]
    utility: float
    utility_ci95: tuple[float, float]


@dataclass(frozen=True)
class Report:
    """The full report: per-scenario rows, the aggregate row, and bootstrap config."""

    agent: str
    rows: list[ScenarioRow]
    aggregate: AggregateRow
    seed: int
    resamples: int


def _percentile(sorted_values: list[float], q: float) -> float:
    """``q``-quantile of pre-sorted values via linear interpolation (Hyndman-Fan type 7)."""
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = q * (len(sorted_values) - 1)
    low = int(pos)
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (pos - low)


def _bootstrap_ci95(rates: list[float], *, seed: int, resamples: int) -> tuple[float, float]:
    """Percentile bootstrap 95% CI of the mean, resampling scenarios with replacement.

    Deterministic: the RNG is seeded, so a given (rates, seed, resamples) always
    yields the same interval. With one scenario every resample is identical and
    the interval collapses to a point — shown openly rather than hidden.
    """
    rng = random.Random(seed)
    n = len(rates)
    means = sorted(sum(rates[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples))
    return _percentile(means, 0.025), _percentile(means, 0.975)


def build_report(
    agent: str, *, seed: int = BOOTSTRAP_SEED, resamples: int = BOOTSTRAP_RESAMPLES
) -> Report:
    """Score ``agent`` on every scenario in ``ALL_SCENARIOS`` and aggregate the rates."""
    run = AGENTS[agent]
    rows: list[ScenarioRow] = []
    for scenario in ALL_SCENARIOS:
        result = score(run(scenario), scenario)
        rows.append(ScenarioRow(scenario.id, result.disclosure_rate, result.utility))
    disclosure = [row.disclosure_rate for row in rows]
    utility = [row.utility for row in rows]
    aggregate = AggregateRow(
        disclosure_rate=sum(disclosure) / len(disclosure),
        disclosure_ci95=_bootstrap_ci95(disclosure, seed=seed, resamples=resamples),
        utility=sum(utility) / len(utility),
        utility_ci95=_bootstrap_ci95(utility, seed=seed, resamples=resamples),
    )
    return Report(agent, rows, aggregate, seed, resamples)


def render_text(report: Report) -> str:
    """Compact markdown table: one row per scenario, then the aggregate row with CIs."""
    agg = report.aggregate
    dr = f"{agg.disclosure_rate:.2f} [{agg.disclosure_ci95[0]:.2f}, {agg.disclosure_ci95[1]:.2f}]"
    ut = f"{agg.utility:.2f} [{agg.utility_ci95[0]:.2f}, {agg.utility_ci95[1]:.2f}]"
    cells = [
        ("scenario", "disclosure-rate", "utility"),
        *[(r.scenario_id, f"{r.disclosure_rate:.2f}", f"{r.utility:.2f}") for r in report.rows],
        ("**aggregate**", dr, ut),
    ]
    widths = [max(len(cell) for cell in col) for col in zip(*cells, strict=True)]

    def row_line(cells_row: tuple[str, str, str]) -> str:
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells_row, widths, strict=True)) + " |"

    lines = [
        f"[context-leak report] agent={report.agent} scenarios={len(report.rows)} "
        f"bootstrap=(seed={report.seed}, resamples={report.resamples})",
        "",
        row_line(cells[0]),
        "| " + " | ".join("-" * w for w in widths) + " |",
        *[row_line(cells_row) for cells_row in cells[1:]],
        "",
        "aggregate = mean over scenarios; [lo, hi] = bootstrap 95% CI "
        "(scenarios resampled with replacement, seeded).",
    ]
    return "\n".join(lines)


def render_json(report: Report) -> str:
    """JSON rendering of the same report data."""
    agg = report.aggregate
    payload = {
        "agent": report.agent,
        "scenarios": [
            {"id": r.scenario_id, "disclosure_rate": r.disclosure_rate, "utility": r.utility}
            for r in report.rows
        ],
        "aggregate": {
            "disclosure_rate": agg.disclosure_rate,
            "disclosure_rate_ci95": list(agg.disclosure_ci95),
            "utility": agg.utility,
            "utility_ci95": list(agg.utility_ci95),
        },
        "bootstrap": {"seed": report.seed, "resamples": report.resamples},
    }
    return json.dumps(payload, indent=2)


def run_report(agent: str, *, json_out: bool = False) -> int:
    """Build the report for ``agent`` and print it to stdout. Returns 0."""
    report = build_report(agent)
    print(render_json(report) if json_out else render_text(report))
    return 0
