- Income tax API (Task 7, v0.3 2.3): `POST /income-tax/calculate` wraps
  `run_income_tax_module()` with a strict request model (decimal-string
  money, engine enums, optional `requested_policy_version` because the draft
  policy has no version) and a response with outcome, reason code, category,
  missing facts, a null value and a deterministic explanation. The policy is
  draft, so every result is `needs_review` or `unsupported`; no calculated
  amount changes. `GET /api/v1/evidence` now lists `income_tax` with
  `policy_version: null` (the field is nullable); `/meta` is unchanged.
  A negative income is not refused by the request model: the engine reports
  it as `unsupported` (`IT_NEGATIVE_INCOME_NOT_MODELLED`) (D54).
