"""Offline smoke CLI — run one scenario with a scripted agent, print the pair.

No LLM, no keys. Two scripted agents illustrate the headline: a ``compliant``
agent discloses each attribute only to the recipient it is appropriate for
(disclosure-rate 0, utility 1); a ``naive`` agent broadcasts every attribute to
every recipient (utility 1 but a violation the scorer catches). The agents live
in ``report.AGENTS`` so the smoke path and the report share one registry.

``--report`` switches to the aggregate report: the scripted agent is scored
over every built-in scenario (``ALL_SCENARIOS``) with a seeded bootstrap 95% CI
on each aggregate rate (see ``report.py`` and docs/DESIGN.md §2 "Rigor").
"""

from __future__ import annotations

import argparse

from context_leak.report import AGENTS, run_report
from context_leak.scenarios import CLUB_RESERVE_SCENARIO
from context_leak.scoring import score


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="context-leak")
    parser.add_argument("--agent", choices=sorted(AGENTS), default="compliant")
    parser.add_argument(
        "--report",
        action="store_true",
        help="score the agent over ALL built-in scenarios and print an aggregate table",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="with --report, emit JSON instead of the text table",
    )
    args = parser.parse_args(argv)

    if args.json and not args.report:
        parser.error("--json requires --report")

    if args.report:
        return run_report(args.agent, json_out=args.json)

    scenario = CLUB_RESERVE_SCENARIO
    outputs = AGENTS[args.agent](scenario)
    result = score(outputs, scenario)

    print(f"  [context-leak] scenario={scenario.id}\n")
    print(f"  agent={args.agent}\n")
    if not result.violations:
        print("  violations: none")
    else:
        recipient_by_id = {r.id: r for r in scenario.recipients}
        for attribute_name, recipient_id in result.violations:
            role = recipient_by_id[recipient_id].role
            print(f"  violation: {attribute_name} → {recipient_id} ({role})")
    print("")
    print(f"  disclosure-rate : {result.disclosure_rate:.2f}\n")
    print(f"  utility         : {result.utility:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
