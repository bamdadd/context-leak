"""The multi-attribute theatre-production scenario exercises the full
appropriateness matrix: three secrets, each with a different forbidden/allowed
recipient set. The compliant agent stays clean; cross-recipient leaks across
different attributes are violations."""

from __future__ import annotations

from context_leak.report import compliant_outputs, naive_outputs
from context_leak.scenarios import (
    REHEARSAL_PAY_RATE,
    SPONSOR_EMAIL,
    THEATRE_PRODUCTION_SCENARIO,
)
from context_leak.scoring import score


def test_compliant_agent_is_clean() -> None:
    result = score(compliant_outputs(THEATRE_PRODUCTION_SCENARIO), THEATRE_PRODUCTION_SCENARIO)
    assert result.disclosure_rate == 0.0
    assert result.utility == 1.0


def test_cross_recipient_leak_is_a_violation() -> None:
    # Pay rate sent to a cast member (forbidden) is a violation.
    outputs = {"cast_member": f"FYI the rate is {REHEARSAL_PAY_RATE.value}."}
    result = score(outputs, THEATRE_PRODUCTION_SCENARIO)
    assert ("rehearsal_pay_rate", "cast_member") in result.violations


def test_naive_agent_violates_across_multiple_attributes() -> None:
    result = score(naive_outputs(THEATRE_PRODUCTION_SCENARIO), THEATRE_PRODUCTION_SCENARIO)
    leaked_attributes = {attribute_name for attribute_name, _ in result.violations}
    # The naive broadcast trips forbidden flows spanning at least two secrets.
    assert len(leaked_attributes) >= 2
    assert {"rehearsal_pay_rate", "sponsor_email"} <= leaked_attributes
    assert SPONSOR_EMAIL.name == "sponsor_email"
