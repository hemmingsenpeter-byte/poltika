# Review of the Q71-Q140 question-set run (26 September 2026)

- **Reviewed:** a Claude Code session's run of Q71-Q140 at `5a73539`. Its
  script and raw results are in that session's scratchpad and are not in
  the repository; the session offered to add them.
- **Reviewer:** Claude Code, at Pete's request ("review these and apply
  fixes where there are errors").

## Arithmetic spot-checked by hand

- **FTC:** Q76-Q79 and Q80-Q82 all reproduce. FTC reaches zero at $97,173,
  because 52,273 complete dollars × 0.275 = $14,375.075. The residues passed
  to IWTC ($0.075 and $0.35) and the $42,027.50 at $250,000 also check out.
- **Best Start:** Q115 (zero at $98,243; $0.18 at $98,242) reproduces.
- **AS:** Q122-Q124 and Q131-Q133 reproduce: $93.01 → $1; $241.57 →
  $104; $241.58 → $105; $620 → $291; the $305 cap. So do Q137 (107
  imputed dollars; $283 at an income of $1,100) and Q138 ($248).

## Errors found and fixed (this PR)

| Item | Classification | Fix |
| --- | --- | --- |
| **Q135:** assets exactly at the r 15 ceiling were `unsupported` | SPEC_ERROR + CODE_ERROR + TEST_ERROR | The official Regulations text (latest version, checked 26 September 2026) says cash assets **"must not exceed"** $16,200 / $8,100 (r 15(1)), so assets at the ceiling meet the requirement. The comparison `>=` became `>`, and the specification wording was corrected. The protected spec case `asset_ceiling_met_is_unsupported` ($8,100) was replaced by `asset_ceiling_exceeded_is_unsupported` ($8,100.01) and `asset_ceiling_exactly_met_is_eligible` ($8,100 → $75, hand-derived). Four other tests had used exactly $8,100 as "failing"; they now use $8,100.01, and the acceptance boundary test treats offset 0 as eligible. **The report's Q135 answer ($16,200 → unsupported) is therefore wrong; the correct answer is eligible.** $16,200.01 remains unsupported. |
| **QS-5:** MFTC `excluded` full-time-earner weeks gave the reason for a different case | CODE_ERROR (reason text) | The reason now covers "not a full-time earner for every week" as well as the ME 2(2)-(4) case. **The outcome stays `unsupported`:** whether an evidenced "not a full-time earner" should instead be $0 (the specification says an evidenced failure "may yield zero") is an INTERPRETATION_AMBIGUITY for Pete. |
| **QS-6:** verified $0 accommodation costs gave a calculated $0 | SPEC gap + CODE_ERROR | Specification step 1 and AS-01 (s 65AAA) require accommodation costs, so $0 costs are now `unsupported` (an evidenced exclusion, like the r 15 ceiling). The generated acceptance test now draws costs from 1 cent. |

## No change needed

The scope limits the report lists are genuine v0.1 limits, not defects:

- "Doesn't qualify for the whole year" can't tell part-year apart from never
  qualifying.
- AS has no rule for a change in the middle of a week.
- Conflicting candidate values aren't evaluated.
- Conflicting evidence within one policy isn't detected.
- There is no duplicate-child detection.

## For Pete

- **QS-5:** should an evidenced "not a full-time earner" give MFTC $0, or
  stay `unsupported`? *Resolved 26 September 2026 by WFF DEC-001: it stays
  `unsupported`. ME 1(3)(c) pro-rates MFTC by full-time-earner week, so it
  is a part-year amount, not $0. QS-6's $0 accommodation costs are now
  `ineligible` $0 (AS DEC-005).*
