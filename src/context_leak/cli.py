"""Offline smoke CLI — run one scenario with a scripted agent, print the pair.

No LLM, no keys. Two scripted agents illustrate the headline: a ``compliant``
agent discloses each attribute only to the recipient it is appropriate for
(disclosure-rate 0, utility 1); a ``naive`` agent broadcasts every attribute to
every recipient (utility 1 but a violation the scorer catches).
"""

from __future__ import annotations

import argparse

from context_leak.scenarios import CLUB_RESERVE_SCENARIO
from context_leak.scoring import score
from context_leak.types import Scenario


def _compliant_outputs(scenario: Scenario) -> dict[str, str]:
    """Disclose each attribute only along its appropriate flow."""
    attr_by_name = {a.name: a for a in scenario.attributes}
    outputs: dict[str, str] = {}
    for attribute_name, recipient_id in scenario.appropriate_flows:
        value = attr_by_name[attribute_name].value
        outputs[recipient_id] = f"{outputs.get(recipient_id, '')} {value}".strip()
    return outputs


def _naive_outputs(scenario: Scenario) -> dict[str, str]:
    """Broadcast every attribute value to every recipient."""
    everything = " ".join(a.value for a in scenario.attributes)
    return {r.id: everything for r in scenario.recipients}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="context-leak")
    parser.add_argument("--agent", choices=["compliant", "naive"], default="compliant")
    args = parser.parse_args(argv)

    scenario = CLUB_RESERVE_SCENARIO
    outputs = (
        _compliant_outputs(scenario) if args.agent == "compliant" else _naive_outputs(scenario)
    )
    result = score(outputs, scenario)

    print(f"[context-leak] scenario={scenario.id} agent={args.agent}")
    print(f"  disclosure-rate : {result.disclosure_rate:.2f}  violations={result.violations}")
    print(f"  utility         : {result.utility:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
