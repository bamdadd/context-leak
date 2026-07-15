"""Trivial import test: the package imports and the frozen contract is present.

The fuller smoke test is owned by another workstream — this only proves the
scaffold is green.
"""

import context_leak
from context_leak.types import Attribute, Recipient, Scenario, Scorer, ScoreResult


def test_import() -> None:
    assert context_leak.__version__


def test_contract_symbols_exist() -> None:
    assert Attribute and Recipient and Scenario and ScoreResult and Scorer
