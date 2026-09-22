"""Runs INSIDE a throwaway venv with only the built `poltika` wheel (plus
`httpx`) installed -- no source checkout on `sys.path`, no dev extras
beyond `httpx` (needed for `TestClient`). Deliberately self-contained: no
import of `tests.conftest` or anything else from the checkout that ran
this script, since the whole point is proving the *installed artifact*
works standalone. The request payload below is a hand-copied literal
matching `spec_cases.yaml`'s `single_ordinary_low_income` case, not loaded
from that YAML file (which isn't installed -- `policy_specs/` is supplied
via `POLTIKA_POLICY_SPECS_DIR`, set by the parent test before this script
runs, per ADR-0011).

Prints `PROBE_OK` and exits 0 on success; prints the failure and exits 1
otherwise -- the parent test (`test_installed_artifact.py`) checks both.
"""

from __future__ import annotations

import sys

from fastapi.testclient import TestClient

from poltika.api.main import app

PAYLOAD = {
    "modelled_date": "2026-06-01",
    "requested_policy_version": "0.1.0",
    "household_eligibility": "verified",
    "extra_instalment_status": "verified",
    "partner_status": "single",
    "family_scheme_income": {"claimant_amount": "30000"},
    "net_family_scheme_income": "30000",
    "net_family_scheme_income_me3_attested": True,
    "in_work_eligibility": "verified",
    "ftc_iwtc_protected_or_direct_abatement": "verified",
    "mc6a_veterans_payment": "verified",
    "mc6b_disqualifying_payment": "verified",
    "minimum_family_full_time_earner_weeks": "verified",
    "best_start_no_shared_care": "verified",
    "best_start_protected_credit": "verified",
    "children": [
        {
            "qualifies_whole_year": "verified",
            "best_start_cohort": "outside_best_start_entitlement",
            "best_start_no_disqualifying_payment": "verified",
        }
    ],
}


def main() -> int:
    with TestClient(app) as client:
        response = client.post("/wff/calculate", json=PAYLOAD)

    if response.status_code != 200:
        print(f"PROBE_FAILED: status {response.status_code}: {response.text}")
        return 1

    body = response.json()
    ftc = body.get("family_tax_credit", {})
    if ftc.get("outcome") != "calculated" or ftc.get("value") is None:
        print(f"PROBE_FAILED: unexpected family_tax_credit shape: {ftc}")
        return 1

    print("PROBE_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
