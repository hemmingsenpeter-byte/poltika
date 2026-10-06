# Integration train, 6 October 2026 — final-head review coverage

Claude Code (Opus 5.5) ran the train as the sole merger (D18). Each PR merged
by squash with green required CI on an up-to-date branch and no bypass. Per-PR
detail is in each PR's comments. The source PRs have their own records
(`2026-10-06-pr148.md`, `pr151.md`, `pr172.md`, `pr175.md`).

| PR | Squash | Authorship | Final-head review coverage |
| --- | --- | --- | --- |
| #171 entities | `b176ddc` | Claude draft; Codex recovery and singleton fix; Claude restack | Claude orchestrator review plus `poltika-reviewer` at `486f376`: no P1/P2. 335 tests; 8 mutations caught. P3 citation `:52` → `:50` fixed in the records PR. Claude parts had same-model review only (not a rule-4 path) |
| #174 XLSX DTD guard | `0d115b4` | Claude parser; Codex D19 correction and tests | Cross-model for `bf51ce2`; same-model plus Codex author-chain probing for the parser. `poltika-reviewer` at `3f43c0b`: no findings. 68 adversarial payloads refused; 19 sheet pins unchanged |
| #176 review rule (replaces #170) | `7c0f67e` | Codex `9b939ce`; Claude `be7ca4e` and `0df6008` | Claude cross-model review of `9b939ce` found R1 (P2). Pete chose the mechanical-update exemption on 6 Oct, which Claude implemented. `poltika-reviewer` approved `0df6008`. The Claude commits await a Codex re-check |
| #164 model governance | `94df1a0` | Claude draft; Codex corrections | Codex check of the draft (`reviews/2026-10-05-pr164.md`). Claude cross-model review of `f91af5c`. `poltika-reviewer` approved `70fc126` with 611 tests and 6 mutations caught. Mechanical update verified |
| #167 approved decisions | `1b64d0e` | Codex; Claude integration commits | Claude cross-model review of `6fcfab5` found R1 (P2: SLP scope attributed to Pete). Pete confirmed the restricted-capacity reading on 6 Oct. `poltika-reviewer` rounds on `912f8e9`, `02e84a4` (D17 fidelity fix) and `52cf02e` (tracker conflict): approve. The Claude commits await a Codex re-check |
| #175 WFF currency | `4c09972` | Codex | See `2026-10-06-pr175.md` |
| #172 disposable income | `30935de` | Codex | See `2026-10-06-pr172.md` |
| #148 income tax | `164fdbd` | Codex | See `2026-10-06-pr148.md` |
| #151 JS/SPS/SLP | `38e5629` | Codex; Claude conflict resolution | See `2026-10-06-pr151.md` |

Closed without merging: #155 (superseded coordinator brief) and #170 (replaced
by #176).

The mechanical-update exemption (ADR-0020, Pete, 6 October 2026) was applied
to #164, #175, #172 and #148, with a patch-id delta check recorded on each PR.
Every conflict resolution (#167 three times: `cb32c81`, `912f8e9`, `52cf02e`; #151) was treated as a fix and
re-reviewed.
