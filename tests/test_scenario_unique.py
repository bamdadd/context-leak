"""Uniqueness guards on Scenario attribute names and recipient ids."""

from __future__ import annotations

import pytest

from context_leak.scenarios import CLUB_RESERVE_SCENARIO
from context_leak.types import Attribute, Recipient, Scenario


def _base_kwargs() -> dict:
    return {
        "id": "unique-fixture",
        "description": "Fixture for uniqueness validation.",
        "attributes": [
            Attribute(name="a", value="1"),
            Attribute(name="b", value="2"),
        ],
        "recipients": [
            Recipient(id="r1", role="one"),
            Recipient(id="r2", role="two"),
        ],
        "forbidden": [],
        "task": "noop",
        "appropriate_flows": [],
    }


def test_duplicate_attribute_name_raises() -> None:
    kwargs = _base_kwargs()
    kwargs["attributes"] = [
        Attribute(name="dup", value="1"),
        Attribute(name="dup", value="2"),
    ]
    with pytest.raises(ValueError, match="duplicate attribute name: 'dup'"):
        Scenario(**kwargs)


def test_duplicate_recipient_id_raises() -> None:
    kwargs = _base_kwargs()
    kwargs["recipients"] = [
        Recipient(id="same", role="one"),
        Recipient(id="same", role="two"),
    ]
    with pytest.raises(ValueError, match="duplicate recipient id: 'same'"):
        Scenario(**kwargs)


def test_clean_scenario_still_builds() -> None:
    scenario = Scenario(**_base_kwargs())
    assert scenario.id == "unique-fixture"
    # Built-in scenarios must continue to construct without error.
    assert CLUB_RESERVE_SCENARIO.id == "club-reserve-quarterly"
