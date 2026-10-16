- Income tax reads the shared household model (Task 7, BUILD_PLAN_v0_3.md
  2.3): `to_income_tax()` maps one person's own facts (`IncomeTaxFacts`,
  the nine `policy_specs/income_tax/facts.yaml` questions apart from the
  amount) and their `it_annual_taxable` income spells for the tax year to
  the engine's scenario. Spells must tile the year: a gap is unknown and a
  spell past the year is refused (Q10), never apportioned. Taxable income
  is never derived from earnings or another policy's basis (IT-03).
  `run_household_income_tax()` keeps the engine's order, so a known
  exclusion is `unsupported` before any mapping refusal, and
  `household_from_income_tax()` holds an engine scenario as a one-person
  household. All 47 draft spec cases round-trip to identical scenarios and
  results. A household without tax facts keeps its content hash. The
  engine is unchanged and no calculated amount changes.
