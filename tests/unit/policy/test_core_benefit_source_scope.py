"""Keep approved source-scope exclusions visible before engines exist."""

from pathlib import Path

import pytest
import yaml

from poltika.semantics.schemas.source_catalog import SourceCatalog

POLICY_ROOT = Path(__file__).resolve().parents[3] / "policy_specs"


@pytest.mark.parametrize(
    "policy", ("jobseeker_support", "sole_parent_support", "supported_living_payment")
)
def test_own_right_benefits_for_both_partners_remain_explicitly_unsupported(policy: str) -> None:
    """The single-person scope must not imply household-wide legal ineligibility."""
    raw = yaml.safe_load((POLICY_ROOT / policy / "sources.yaml").read_text())
    catalog = SourceCatalog.model_validate(raw)
    assert catalog.model_extra is not None
    limits = {entry["id"]: entry for entry in catalog.model_extra["coverage_limits"]}
    limit = limits["both_partners_main_benefits_in_own_right"]
    assert limit["outcome"] == "unsupported"
    assert limit["category"] == "not_modelled"
    assert limit["precedence"] == "before_needs_review"
    assert catalog.by_id()[limit["source_id"]].authority_rank == 1
    assert ((POLICY_ROOT / policy) / limit["approval_record"]).is_file()
