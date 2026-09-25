"""v0.1.5 Phase 1: the source catalogue (`policy_specs/<policy>/sources.yaml`)
as a validated model, with an authority rank for every source.

The rank is derived from each entry's existing `kind` rather than written
into every entry (plan adjustment 1: one catalogue, not two). Lower is more
authoritative:

1. legislation (including amending legislation)
2. regulation or order
3. official operational material (published rate tables, area lists)
4. official guidance (including worked examples and interpretation)

Ranks 5-7 (Cabinet or policy documents, secondary material, Poltika
assumptions) are reserved; no v0.1 source has them. Guidance never outranks
statute. A `kind` not listed here fails validation, so a new kind of source
must be ranked deliberately before it can be cited.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, model_validator


class SourceKind(str, Enum):
    LEGISLATION = "legislation"
    AMENDING_LEGISLATION = "amending_legislation"
    FUTURE_AMENDING_LEGISLATION = "future_amending_legislation"
    REGULATIONS = "regulations"
    AGENCY_RATES = "agency_rates"
    AGENCY_GEOGRAPHY = "agency_geography"
    AGENCY_GUIDANCE = "agency_guidance"
    AGENCY_GUIDANCE_AND_EXAMPLE = "agency_guidance_and_example"
    AGENCY_GUIDANCE_AND_EXAMPLES = "agency_guidance_and_examples"
    AGENCY_WORKED_EXAMPLE = "agency_worked_example"
    AGENCY_WORKED_EXAMPLES = "agency_worked_examples"
    AGENCY_INTERPRETATION = "agency_interpretation"
    AGENCY_CHANGE_NOTICE = "agency_change_notice"


class SourceType(str, Enum):
    LEGISLATION = "legislation"
    REGULATION_OR_ORDER = "regulation_or_order"
    OFFICIAL_OPERATIONAL = "official_operational"
    OFFICIAL_GUIDANCE = "official_guidance"


_RANKS: dict[SourceType, int] = {
    SourceType.LEGISLATION: 1,
    SourceType.REGULATION_OR_ORDER: 2,
    SourceType.OFFICIAL_OPERATIONAL: 3,
    SourceType.OFFICIAL_GUIDANCE: 4,
}

SOURCE_TYPES: dict[SourceKind, SourceType] = {
    SourceKind.LEGISLATION: SourceType.LEGISLATION,
    SourceKind.AMENDING_LEGISLATION: SourceType.LEGISLATION,
    SourceKind.FUTURE_AMENDING_LEGISLATION: SourceType.LEGISLATION,
    SourceKind.REGULATIONS: SourceType.REGULATION_OR_ORDER,
    SourceKind.AGENCY_RATES: SourceType.OFFICIAL_OPERATIONAL,
    SourceKind.AGENCY_GEOGRAPHY: SourceType.OFFICIAL_OPERATIONAL,
    SourceKind.AGENCY_GUIDANCE: SourceType.OFFICIAL_GUIDANCE,
    SourceKind.AGENCY_GUIDANCE_AND_EXAMPLE: SourceType.OFFICIAL_GUIDANCE,
    SourceKind.AGENCY_GUIDANCE_AND_EXAMPLES: SourceType.OFFICIAL_GUIDANCE,
    SourceKind.AGENCY_WORKED_EXAMPLE: SourceType.OFFICIAL_GUIDANCE,
    SourceKind.AGENCY_WORKED_EXAMPLES: SourceType.OFFICIAL_GUIDANCE,
    SourceKind.AGENCY_INTERPRETATION: SourceType.OFFICIAL_GUIDANCE,
    SourceKind.AGENCY_CHANGE_NOTICE: SourceType.OFFICIAL_GUIDANCE,
}


class SourceEntry(BaseModel):
    """One catalogue entry. Check evidence (dated `*_check` fields, notes)
    is carried as extra fields, unmodelled, as the provenance report
    already reads it."""

    model_config = ConfigDict(extra="allow")

    id: str
    kind: SourceKind
    title: str
    url: str

    @property
    def source_type(self) -> SourceType:
        return SOURCE_TYPES[self.kind]

    @property
    def authority_rank(self) -> int:
        return _RANKS[self.source_type]


class SourceCatalog(BaseModel):
    model_config = ConfigDict(extra="allow")

    sources: list[SourceEntry]

    @model_validator(mode="after")
    def _unique_ids(self) -> SourceCatalog:
        ids = [s.id for s in self.sources]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate source id(s) in the catalogue: {duplicates}")
        return self

    def by_id(self) -> dict[str, SourceEntry]:
        return {s.id: s for s in self.sources}
