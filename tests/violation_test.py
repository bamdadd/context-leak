from pytest import CaptureFixture

from context_leak.cli import main


def test_cli_prints_no_violations(capsys: CaptureFixture[str]) -> None:
    exit_code = main(["--agent", "compliant"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "violations: none" in output


def test_cli_prints_violation_with_recipient_role(
    capsys: CaptureFixture[str],
) -> None:
    exit_code = main(["--agent", "naive"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert ("violation: reserve_balance → general_member (general club member)") in output

    assert "1: reserve_balance" not in output
