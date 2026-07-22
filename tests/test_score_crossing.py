"""Direct tests for score()'s crossing logic: forbidden × per-recipient output
→ violations, and the disclosure_rate / utility arithmetic with its empty
guards. test_scoring.py covers the disclosed()/normalization side; this covers
the matrix crossing."""

from __future__ import annotations

from context_leak.scoring import score
from context_leak.types import Attribute, Recipient, Scenario

_SECRET = Attribute("balance", "$47,318.22")


def _scenario(forbidden: list[tuple[str, str]], appropriate: list[tuple[str, str]]) -> Scenario:
    return Scenario(
        id="s",
        description="d",
        attributes=[_SECRET],
        recipients=[Recipient("insider", "manager"), Recipient("outsider", "vendor")],
        forbidden=forbidden,
        task="t",
        appropriate_flows=appropriate,
    )


def test_forbidden_disclosure_is_a_violation() -> None:
    scenario = _scenario([("balance", "outsider")], [])
    result = score({"outsider": f"The balance is {_SECRET.value}."}, scenario)
    assert result.violations == [("balance", "outsider")]


def test_same_value_to_a_non_forbidden_recipient_is_not_a_violation() -> None:
    # The forbidden pair targets "outsider"; disclosing the same value to
    # "insider" (not forbidden) must not count.
    scenario = _scenario([("balance", "outsider")], [])
    result = score({"insider": f"The balance is {_SECRET.value}."}, scenario)
    assert result.violations == []
    assert result.disclosure_rate == 0.0


def test_appropriate_flow_that_occurred_is_counted() -> None:
    scenario = _scenario([], [("balance", "insider")])
    result = score({"insider": f"balance {_SECRET.value}"}, scenario)
    assert result.appropriate == [("balance", "insider")]
    assert result.utility == 1.0


def test_rate_math_half_of_two_forbidden() -> None:
    scenario = _scenario([("balance", "insider"), ("balance", "outsider")], [])
    # Disclosed to outsider only → 1 of 2 forbidden flows occurred.
    result = score({"outsider": f"{_SECRET.value}"}, scenario)
    assert len(result.violations) == 1
    assert result.disclosure_rate == 0.5


def test_empty_guards() -> None:
    scenario = _scenario([], [])
    result = score({}, scenario)
    assert result.disclosure_rate == 0.0  # no forbidden flows
    assert result.utility == 1.0  # nothing required
