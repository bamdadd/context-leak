"""A Scenario must have unique attribute names and recipient ids — a duplicate
would silently shadow the earlier one in scoring's `{a.name: a}` map."""

from __future__ import annotations

import pytest

from context_leak.scenarios import ALL_SCENARIOS
from context_leak.types import Attribute, Recipient, Scenario


def _scenario(attributes: list[Attribute], recipients: list[Recipient]) -> Scenario:
    return Scenario(
        id="s",
        description="d",
        attributes=attributes,
        recipients=recipients,
        forbidden=[],
        task="t",
        appropriate_flows=[],
    )


def test_duplicate_attribute_name_raises() -> None:
    with pytest.raises(ValueError, match="duplicate attribute name: 'x'"):
        _scenario(
            [Attribute("x", "1"), Attribute("x", "2")],
            [Recipient("r", "role")],
        )


def test_duplicate_recipient_id_raises() -> None:
    with pytest.raises(ValueError, match="duplicate recipient id: 'r'"):
        _scenario(
            [Attribute("x", "1")],
            [Recipient("r", "role"), Recipient("r", "other")],
        )


def test_clean_scenario_still_builds() -> None:
    scenario = _scenario(
        [Attribute("a", "1"), Attribute("b", "2")],
        [Recipient("r1", "role"), Recipient("r2", "role")],
    )
    assert [a.name for a in scenario.attributes] == ["a", "b"]


def test_all_builtin_scenarios_construct() -> None:
    # Reaching this import/collection at all means every built-in scenario
    # passed __post_init__; assert we actually have some.
    assert len(ALL_SCENARIOS) >= 1
