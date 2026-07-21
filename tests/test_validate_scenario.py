"""Tests for scenario matrix validation.

``forbidden``/``appropriate_flows`` are ``(attribute_name, recipient_id)``
pairs, but nothing used to check those names resolve — a typo silently
mis-scored or ``KeyError``-ed deep in scoring. ``validate_scenario`` turns that
into a clear ``ValueError`` naming the offending pair.
"""

from __future__ import annotations

import dataclasses

import pytest

from context_leak.scenarios import CLUB_RESERVE_SCENARIO
from context_leak.scoring import score, validate_scenario
from context_leak.types import Scenario


def test_all_builtin_scenarios_validate() -> None:
    # The shipped scenario is well-formed.
    validate_scenario(CLUB_RESERVE_SCENARIO)


def _with(**changes: object) -> Scenario:
    return dataclasses.replace(CLUB_RESERVE_SCENARIO, **changes)


def test_forbidden_unknown_attribute_raises() -> None:
    good_recipient = CLUB_RESERVE_SCENARIO.recipients[0].id
    scenario = _with(forbidden=[("no_such_attribute", good_recipient)])
    with pytest.raises(ValueError, match="unknown attribute 'no_such_attribute'"):
        validate_scenario(scenario)


def test_forbidden_unknown_recipient_raises() -> None:
    good_attribute = CLUB_RESERVE_SCENARIO.attributes[0].name
    scenario = _with(forbidden=[(good_attribute, "no_such_recipient")])
    with pytest.raises(ValueError, match="unknown recipient 'no_such_recipient'"):
        validate_scenario(scenario)


def test_appropriate_flows_typo_raises_naming_the_pair() -> None:
    good_recipient = CLUB_RESERVE_SCENARIO.recipients[0].id
    scenario = _with(appropriate_flows=[("typoed_attr", good_recipient)])
    with pytest.raises(ValueError, match=r"appropriate_flows pair \('typoed_attr'"):
        validate_scenario(scenario)


def test_score_rejects_a_mis_authored_scenario() -> None:
    # score() validates first, so a bad matrix fails loud instead of KeyErroring.
    scenario = _with(forbidden=[("nope", "nope")])
    with pytest.raises(ValueError):
        score({}, scenario)
