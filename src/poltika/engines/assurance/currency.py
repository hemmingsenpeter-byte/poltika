"""v0.1.6 Task 2.1: the source-currency report.

Reads one policy's `policy.yaml` and source catalogue as at a date and lists
what needs a person (or GPT/Codex) to recheck. It fetches nothing. Checking
a source stays a reviewed human step (`BUILD_PLAN_v0_1_6.md`).

**Due**, each with a reason:

- a parameter value whose interval ends within `ENDING_WITHIN_DAYS`, or has
  already ended;
- a parameter value still `needs_review`;
- a parameter value with no end date;
- a source cited by a parameter value whose latest structured check (the
  `checked_on` date inside a `*_check` mapping) is missing or older than
  `MAX_CHECK_AGE_DAYS`.

**For information:** sources no parameter cites that have no structured
check. They are cited by rules or used as guidance. They are listed so the
gap is visible, but they don't make the report due.

`python -m poltika.engines.assurance.currency [--as-of YYYY-MM-DD] <policy_dir>...`
(`--as-of` defaults to today in New Zealand)
prints Markdown and exits 0. The weekly workflow opens an issue from it
when anything is due.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml

from poltika.policy.loader import load_policy_spec

ENDING_WITHIN_DAYS = 90
MAX_CHECK_AGE_DAYS = 180


@dataclass
class CurrencyReport:
    policy_id: str
    as_of: date
    due: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)


def last_structured_check(source: dict[str, Any]) -> date | None:
    """The latest `checked_on` date in any `*_check` mapping of a catalogue
    entry. Free-text checks carry no machine-readable date and don't
    count."""
    dates = [
        value["checked_on"]
        for key, value in source.items()
        if key.endswith("_check")
        and isinstance(value, dict)
        and isinstance(value.get("checked_on"), date)
    ]
    return max(dates, default=None)


def currency_report(policy_dir: Path, as_of: date) -> CurrencyReport:
    spec = load_policy_spec(policy_dir / "policy.yaml")
    catalog = yaml.safe_load((policy_dir / spec.source_catalog).read_text())
    report = CurrencyReport(policy_id=spec.policy_id, as_of=as_of)

    horizon = as_of + timedelta(days=ENDING_WITHIN_DAYS)
    cited: set[str] = set()
    for param in spec.parameters:
        for value in param.values:
            cited.add(value.source_id)
            where = f"`{param.id}` from {value.effective_from}"
            if value.effective_to is None:
                report.due.append(f"{where} has no end date")
            elif value.effective_to <= as_of:
                report.due.append(f"{where} ended on {value.effective_to}")
            elif value.effective_to <= horizon:
                days = (value.effective_to - as_of).days
                report.due.append(f"{where} ends on {value.effective_to} ({days} days)")
            if value.review_status.value != "approved":
                report.due.append(f"{where} is `{value.review_status.value}`")

    oldest_allowed = as_of - timedelta(days=MAX_CHECK_AGE_DAYS)
    for source in catalog["sources"]:
        checked = last_structured_check(source)
        sid = source["id"]
        if sid in cited:
            if checked is None:
                report.due.append(f"source `{sid}` (cited by a parameter) has no structured check")
            elif checked < oldest_allowed:
                report.due.append(
                    f"source `{sid}` (cited by a parameter) was last checked on {checked}, "
                    f"more than {MAX_CHECK_AGE_DAYS} days ago"
                )
        elif checked is None:
            report.info.append(f"source `{sid}` has no structured check")
    return report


def render(reports: list[CurrencyReport]) -> str:
    lines = [
        f"# Source currency report, as at {reports[0].as_of}"
        if reports
        else "# Source currency report"
    ]
    lines.append("")
    lines.append(
        f"Due: parameter intervals ending within {ENDING_WITHIN_DAYS} days, values not approved or "
        f"open-ended, and cited sources with no structured check in {MAX_CHECK_AGE_DAYS} days."
    )
    for r in reports:
        lines += ["", f"## {r.policy_id}", "", f"### Due ({len(r.due)})", ""]
        lines += [f"- {item}" for item in r.due] or ["- Nothing due."]
        lines += ["", f"### For information ({len(r.info)})", ""]
        lines += [f"- {item}" for item in r.info] or ["- Nothing."]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    # Policy dates are New Zealand dates.
    today = datetime.now(ZoneInfo("Pacific/Auckland")).date()
    parser.add_argument("--as-of", type=date.fromisoformat, default=today)
    parser.add_argument("policy_dirs", nargs="+", type=Path)
    args = parser.parse_args(argv)
    reports = [currency_report(p, args.as_of) for p in args.policy_dirs]
    sys.stdout.write(render(reports))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
