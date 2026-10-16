- Income tax reads the shared household model (Task 7, BUILD_PLAN_v0_3.md
  2.3): `to_income_tax()` maps one person's own facts (`IncomeTaxFacts`,
  the eight `policy_specs/income_tax/facts.yaml` questions other than the
  amount, with the attestation a strict boolean) and their single
  whole-year `it_annual_taxable` spell, used as given, to the engine's
  scenario. Several spells are refused, never summed (IT-02); no spell is
  unknown; a spell past the year is refused (Q10), never apportioned.
  Taxable income
  is never derived from earnings or another policy's basis (IT-03).
  `run_household_income_tax()` keeps the engine's order, so a known
  exclusion is `unsupported` before any mapping refusal, and
  `household_from_income_tax()` holds an engine scenario as a one-person
  household. All 47 draft spec cases round-trip to identical scenarios and
  results. A household without tax facts keeps its content hash. The
  engine is unchanged and no calculated amount changes.
