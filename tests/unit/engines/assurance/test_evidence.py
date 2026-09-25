"""v0.1.5 Phase 1 and Task 7.4: evidence coverage, and attacks on it."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from poltika.engines.assurance.evidence import evidence_coverage, main
from poltika.semantics.schemas.source_catalog import SourceCatalog, SourceType
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR


@pytest.mark.parametrize("policy_dir", [WFF_POLICY_DIR, AS_POLICY_DIR], ids=["wff", "as"])
def test_real_policies_are_fully_evidenced(policy_dir: Path) -> None:
    report = evidence_coverage(policy_dir)
    assert report["problems"] == []
    summary = report["summary"]
    assert summary["parameter_values_with_ranked_source"] == summary["parameter_values"]
    assert summary["rules_citing_primary_legislation"] == summary["rules"]


def test_statutory_sources_outrank_guidance() -> None:
    catalog = SourceCatalog.model_validate(yaml.safe_load((WFF_POLICY_DIR / "sources.yaml").read_text()))
    ranks = {s.source_type: s.authority_rank for s in catalog.sources}
    assert ranks[SourceType.LEGISLATION] < ranks[SourceType.OFFICIAL_GUIDANCE]


def _copy(tmp_path: Path) -> Path:
    target = tmp_path / "accommodation_supplement"
    shutil.copytree(AS_POLICY_DIR, target)
    return target


def test_a_parameter_resting_on_guidance_is_a_problem(tmp_path: Path) -> None:
    policy_dir = _copy(tmp_path)
    policy = policy_dir / "policy.yaml"
    # as-msd-assets is agency guidance (rank 4).
    policy.write_text(policy.read_text().replace("source_id: as-social-security-regulations", "source_id: as-msd-assets", 1))
    problems = evidence_coverage(policy_dir)["problems"]
    assert any("rank 3 or better is required" in p for p in problems)
    assert main([str(policy_dir)]) == 1


def test_an_unranked_source_kind_is_refused(tmp_path: Path) -> None:
    policy_dir = _copy(tmp_path)
    sources = policy_dir / "sources.yaml"
    sources.write_text(sources.read_text().replace("kind: legislation", "kind: blog_post", 1))
    with pytest.raises(ValidationError):
        evidence_coverage(policy_dir)


def test_a_rule_citing_an_unknown_source_is_a_problem(tmp_path: Path) -> None:
    policy_dir = _copy(tmp_path)
    spec = policy_dir / "specification.md"
    spec.write_text(spec.read_text().replace("`as-msd-areas`", "`as-msd-deleted-page`", 1))
    assert any("unknown source" in p for p in evidence_coverage(policy_dir)["problems"])


def test_a_deleted_source_is_a_problem(tmp_path: Path) -> None:
    policy_dir = _copy(tmp_path)
    catalog = yaml.safe_load((policy_dir / "sources.yaml").read_text())
    catalog["sources"] = [s for s in catalog["sources"] if s["id"] != "as-msd-income-2026"]
    (policy_dir / "sources.yaml").write_text(yaml.safe_dump(catalog, sort_keys=False))
    assert any("unknown source 'as-msd-income-2026'" in p for p in evidence_coverage(policy_dir)["problems"])
