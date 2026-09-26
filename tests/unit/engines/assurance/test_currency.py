"""v0.1.6 Task 2.1: the source-currency report, run against the real
policies at fixed dates so the results don't depend on today's date."""

from __future__ import annotations

from datetime import date

from poltika.engines.assurance.currency import (
    currency_report,
    last_structured_check,
    main,
    render,
)
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR


def test_last_structured_check_takes_the_latest_dated_mapping() -> None:
    source = {
        "id": "x",
        "task_1_check": {"checked_on": date(2026, 1, 1)},
        "task_2_check": {"checked_on": date(2026, 3, 1), "version_checked": date(2027, 1, 1)},
        "task_3_check": "free text, no date",
        "note_check_on": date(2030, 1, 1),  # not a *_check mapping
    }
    assert last_structured_check(source) == date(2026, 3, 1)
    assert last_structured_check({"id": "y", "task_1_check": "text only"}) is None


def test_open_needs_review_value_is_always_due() -> None:
    report = currency_report(WFF_POLICY_DIR, date(2026, 9, 26))
    assert "`in_work_base` from 2026-04-01 is `needs_review`" in report.due


def test_intervals_ending_within_90_days_are_due() -> None:
    before = currency_report(AS_POLICY_DIR, date(2026, 12, 31))  # 91 days before 2027-04-01
    during = currency_report(AS_POLICY_DIR, date(2027, 1, 1))  # 90 days before
    assert not any("ends on" in item for item in before.due)
    ending = [item for item in during.due if "ends on 2027-04-01 (90 days)" in item]
    assert len(ending) == 38  # every AS parameter value


def test_ended_intervals_are_due() -> None:
    report = currency_report(WFF_POLICY_DIR, date(2027, 4, 1))
    assert sum("ended on 2027-04-01" in item for item in report.due) == 10


def test_stale_check_of_a_cited_source_is_due() -> None:
    # Every structured check in the catalogues is dated 2026-09-24.
    fresh = currency_report(AS_POLICY_DIR, date(2027, 3, 23))  # 180 days later
    stale = currency_report(AS_POLICY_DIR, date(2027, 3, 24))
    assert not any("last checked" in item for item in fresh.due)
    assert any("last checked on 2026-09-24" in item for item in stale.due)


def test_uncited_sources_are_information_only() -> None:
    report = currency_report(AS_POLICY_DIR, date(2026, 9, 26))
    assert report.info
    assert not any(item in report.due for item in report.info)


def test_render_and_cli(capsys) -> None:  # type: ignore[no-untyped-def]
    text = render([currency_report(WFF_POLICY_DIR, date(2026, 9, 26))])
    assert text.startswith("# Source currency report, as at 2026-09-26")
    assert "## working_for_families" in text
    assert main(["--as-of", "2026-09-26", str(WFF_POLICY_DIR), str(AS_POLICY_DIR)]) == 0
    out = capsys.readouterr().out
    assert "## accommodation_supplement" in out
