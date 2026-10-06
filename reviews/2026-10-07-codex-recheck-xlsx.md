# Codex recheck of PR #174 XLSX XML guard — 7 October 2026

## Findings

**Verdict: changes requested — R1 · P2 · CODE_ERROR.** Malformed DTD/entity input can make Expat fail before its refusal callback; the swallowed error then sends the bytes to ElementTree. This violates the stated before-parse contract. The reproduced inputs all end in ElementTree `ParseError`; no successful entity expansion or external-resource access was demonstrated.

Label: independent GPT/Codex review of Claude-authored changes, with commit-level scope. This pass covers the guard and original pin/part tests authored by Claude in `427e6b6` and `ad4ca88`. R1 leaves their follow-up in `review_packets/review_queue.md` open. This is not acceptance authority and does not supply cross-model clearance for the Codex follow-up `bf51ce2`.

## Review inputs

- Reviewer: Codex, fresh delegated review context; date: 7 October 2026.
- PR: [#174](https://github.com/hemmingsenpeter-byte/poltika/pull/174).
- Exact integrated target: `a8b214f05c7aa7380fb0ca0adfd68c30c81bf06d`.
- Claude implementation: `427e6b6a54505ff88a79c7b61a3e0ef5264b2f1e`; parent `d501dfaa3488eb0d278f914c1237f0af8cfb58f3`.
- Claude part-test/docstring commit: `ad4ca8811614db72cd1da603755351a412311565`; parent `427e6b6a54505ff88a79c7b61a3e0ef5264b2f1e`.
- Codex follow-up: `bf51ce23081487febb7b07214d649b46574ef118` (D19 reference correction and additional encoding/preparse/malformed tests). It did not alter the guard algorithm.
- Final PR head: `3f43c0b4966c960cf1878bdc8459de3ac8c706d2`; squash: `0d115b4e2c63b5d6f2d6517d92f74d9d9ffdc934`; main parent/base for the merged diff: `b176ddc72eefd1811a0b8317d812dd389e6f3ae7`.
- Full merged diff reviewed: `0d115b4^..0d115b4`, three files, 300 insertions / 6 deletions. The reader and its pin tests are unchanged from the squash to the exact integrated target.
- Initial worktree: `/private/tmp/poltika-codex-closeout-rechecks-20261007`. The parent lane advanced its documentation branch to `854af8871c9cc69b6495582ec981784e49d9a1db`; an exact-head assertion stopped a second probe attempt. Source/test tree identities were checked: `src` = `9d755281f0c5522f9215f24fd1a760b619227444`, `tests` = `4f2a7ec52d6b9dbf4793ea3c257a6c14d16a42ee` on both revisions. Final checks ran in the parent-created detached `/private/tmp/poltika-codex-merged-recheck-a8b214f`, with an exact-head assertion.
- Contracts/guidance: applicable `AGENTS.md`; current programme authority and orientation; historical BUILD_PLAN frozen roles/source/data/test/review anchors; relevant ARCHITECTURE data-acquisition contract and REPOSITORY_STRUCTURE data/review placement and boundary; review, test, IP and development doctrines; `.claude/skills/pr-review/SKILL.md`, checklist and writing-findings reference; author-preflight distinction.
- Source/spec scope: no statutory rule, rate, threshold, effective date or protected statutory expected value changes. No external policy engine was inspected.
- Rationale exposure: the assignment supplied the intended security contract and helper name. The contract was recorded in `/private/tmp/poltika-codex-xml-contract.md` before implementation, commit rationale or earlier review evidence was read. This is contract-first, not a claim of a fully blind review.

## Independent review

### Independently derived expected behaviour

- Refuse any DTD/entity declaration before ElementTree parses the XML part, across supported XML encodings and every part the reader parses.
- Apply that guarantee to malformed documents/declarations as well as valid documents. Invalid input may fail closed with a reader/parser error; failed guard validation must not be followed by an ElementTree parse of those bytes.
- Preserve stored cell text, all 19 canonical sheet SHA-256 pins/cell counts and the three workbook hashes, comparing to the reader before the guard.
- Preserve the raw-snapshot checksum boundary. `DataContext` checks SHA immediately before the transformation; IRD and MSD transformations call `read_sheet`.

### Discrepancies

| ID | Severity / proposed Review Doctrine class | Trigger and actual behaviour | Impact / resolution |
| --- | --- | --- | --- |
| R1 | P2 / CODE_ERROR | `src/poltika/data/xlsx.py:54`: Expat rejects a standalone `<!ENTITY a "test">` or a malformed prefix/header before its declaration callback, the error is swallowed, and `ElementTree.fromstring` is called. Confirmed for all four workbook part routes. | Narrow breach of the promised pre-parse boundary and the docstring at line 44. These probes remain invalid to ElementTree and raise `ParseError`; no accepted malicious XML was found. Open: fail closed on Expat validation errors and add a regression that traps ElementTree for malformed declaration input. |

Minimal reproduction on `a8b214f05c7aa7380fb0ca0adfd68c30c81bf06d`, from the detached exact-main worktree:

```sh
env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 \
  /private/tmp/poltika-codex-closeout-rechecks-20261007/.venv/bin/python -I -S - <<'PY'
import importlib.util
from xml.etree import ElementTree
spec = importlib.util.spec_from_file_location('reader', 'src/poltika/data/xlsx.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
raw = b'<!ENTITY a "test"><x/>'
original = ElementTree.fromstring
calls = []
def observe(data):
    calls.append(data)
    return original(data)
ElementTree.fromstring = observe
try:
    reader._fromstring(raw)
except ElementTree.ParseError as error:
    print(type(error).__name__, str(error))
finally:
    ElementTree.fromstring = original
print('ElementTree calls:', len(calls))
PY
```

```text
ParseError syntax error: line 1, column 0
ElementTree calls: 1
```

A complete valid DTD following an invalid prefix (`b'!<!DOCTYPE x [<!ENTITY a "test">]><x>&a;</x>'`) also reaches ElementTree, then raises `ParseError` at line 1, column 0. An invalid SYSTEM header (`b'<!DOCTYPE x SYSTEM><x/>'`) reaches ElementTree and raises `ParseError` at column 18. A recognized doctype with a malformed or truncated internal subset is refused before parsing, showing the distinction: only failures before the callback take the fallback.

Suggested correction: on `expat.ExpatError`, raise a parser error without invoking ElementTree; preserve the `ElementTree.ParseError` interface and the Expat diagnostic/code/position if callers rely on them. Pin malformed DTD/entity inputs with an ElementTree-call trap, including the four actual part routes. This does not require a new dependency or changing any sheet pin.

## Author response

Read after the independent contract: D19 and the squash rationale promise refusal of any DTD/entity before ElementTree and preservation of malformed XML `ParseError`. The integration-train record reports historical 68-payload and 19-pin checks on the earlier PR head; those are prior author-chain evidence, not this pass's results. They do not address R1's early Expat error fallback.

No author response to R1 has been requested or posted.

## Resolution and verification

R1 remains open. No source fix was made. Review clearance requires a fix and review of its final head; the 44 green tests do not pin the malformed declaration boundary.

On exact integrated main, Python `3.12.14`, Expat `2.8.4`:

```sh
env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 \
  /private/tmp/poltika-codex-closeout-rechecks-20261007/.venv/bin/python \
  -I -S -u /private/tmp/poltika-codex-xml-probe.py

env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  /private/tmp/poltika-codex-closeout-rechecks-20261007/.venv/bin/python \
  -m pytest -q -p no:cacheprovider tests/unit/data/test_xlsx_pinned.py
```

- Probe: exit 0. 512 declared-encoding/DTD combinations across 64 encodings; all 424 combinations ElementTree accepts are refused before its call. The remaining 88 combinations are also unsupported by baseline ElementTree (48 raise unsupported-multibyte `ValueError`; 40 reach ElementTree and raise parsing errors). No supported valid-document bypass was found.
- Valid DTD part routes: all 24 combinations (four parts × UTF-8, UTF-16, UTF-16LE, UTF-16BE, ISO-8859-1 and CP1252) refused with `XlsxError`.
- Four UTF-8-BOM/UTF-16/no-declaration endian probes refused before ElementTree. Declaration-shaped text in a comment, CDATA or processing instruction remains accepted.
- Fifteen malformed/plain-invalid probes: two recognized DTDs refused; thirteen reach ElementTree and raise `ParseError`. Some are declaration fragments or lookalikes rather than complete declarations; R1 relies on the complete standalone ENTITY and complete DTD after invalid prefix. Standalone ENTITY reaches ElementTree on all four actual part routes.
- Tests bite: a source copy in scratch with only `guard.Parse` disabled defeats all 12 sampled before-parse assertions. Production files were never mutated for this check.
- Pin comparison: all 19 current sheets equal both the reader from `b176ddc72eefd1811a0b8317d812dd389e6f3ae7` and the committed canonical JSON digests/cell counts. All three raw workbook hashes match. Detailed evidence follows below.
- Committed XLSX tests: **44 passed**, no skips; one existing duplicate-ZIP-entry warning from `test_every_part_read_refuses_a_dtd`.
- Scratch probe/result artifacts: `/private/tmp/poltika-codex-xml-probe.py`, `/private/tmp/poltika-codex-xml-results.json`. The reproducible core and durable results are recorded here.
- Full merged diff whitespace check: `git diff --check 0d115b4^ 0d115b4` passed.

### Not verified

The parent lane runs the broad CI-equivalent suite and live GitHub checks centrally; they were not duplicated in this bounded pass. No deploy, external-resource fetch or unbounded entity-expansion stress test was run. The tested supported XML variants are determined by baseline ElementTree on Python 3.12.14; this does not claim results for other interpreter/Expat versions.

Interpreter startup initially stalled in the inherited environment. A clean environment resolved it; all final dynamic results above completed. The discarded attempt stopped by the exact-head assertion is not counted as a check.

Nothing outside this assigned record and reviewer scratch files was edited. No source fixes, statutory values, posts, commits, merges, shared Git mutations or cleanup were performed by this reviewer.

### Digest evidence

Workbook aliases: IRD v1/v2 are `data/raw/ird/ird_working_for_families_statistics/v{1,2}/working-for-families-statistics.xlsx`; MSD v1 is `data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx`.

| Workbook | Raw SHA-256 |
| --- | --- |
| IRD v1 | `d94bb1b27c86f2206208cf54edfdc7dc285aa25398030457dbb04a1bcb8bce2d` |
| IRD v2 | `d94bb1b27c86f2206208cf54edfdc7dc285aa25398030457dbb04a1bcb8bce2d` |
| MSD v1 | `90cd8e7c8ff210ca9334eb035dfef3a39abdefe10365e5f7a6ccbd4291248f74` |

Every row below matched current, pre-guard and committed pin expectations.

| Workbook | Sheet | Cells | Canonical JSON SHA-256 |
| --- | --- | ---: | --- |
| IRD v1 | Explanatory notes | 0 | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| IRD v1 | Working for familes parameters | 415 | `272c07731dfd36f00211debf70e58809e3448e121a437423a84d3d83d3e4a6e0` |
| IRD v1 | Working for families charts | 0 | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| IRD v1 | Working for families data | 797 | `00419cc4f93b6b50bac56576a69a0f7192db2dacba9e3a8df97d594d26633adf` |
| IRD v1 | Working for families income | 2236 | `becfe8c492e473990938e7d9dcfa8c2469726e3c121f298dd874571c0c1be91f` |
| IRD v2 | Explanatory notes | 0 | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| IRD v2 | Working for familes parameters | 415 | `272c07731dfd36f00211debf70e58809e3448e121a437423a84d3d83d3e4a6e0` |
| IRD v2 | Working for families charts | 0 | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| IRD v2 | Working for families data | 797 | `00419cc4f93b6b50bac56576a69a0f7192db2dacba9e3a8df97d594d26633adf` |
| IRD v2 | Working for families income | 2236 | `becfe8c492e473990938e7d9dcfa8c2469726e3c121f298dd874571c0c1be91f` |
| MSD v1 | Contents and notes | 46 | `974cc159388bb2e7bedc2b2c6fc9e93d04f853d2dc2dc9324a3817341206a462` |
| MSD v1 | Summary table-current | 264 | `cd812ef3000302ca2cbb89368b3e1ae7dbc20834180a85717cf3e6afb824f8ea` |
| MSD v1 | Summary table - last 5 years | 134 | `3cce90a85240d3ccd107f350a744a2ceec019b87332cf63c727f772ead2f330b` |
| MSD v1 | Main benefits - last 5 years | 424 | `2da53d7b580f448153e76efa90f2a053193e73397ee7007ba1fdc13a758a1b6d` |
| MSD v1 | JS - last 5 years | 602 | `662e1c223e81d453c7aed88b88229dcc435cf27096dbedb45575a5e5635afd27` |
| MSD v1 | SPS - last 5 years | 469 | `5e413db82b280da28706f23dc8f95750ebe1db1b991d9bc7b5e0ea3f4bdc93fa` |
| MSD v1 | SLP - last 5 years | 646 | `1b0f19136370c95303250b746aa41142cfdcda413b105af320014a3d6f7233f8` |
| MSD v1 | Other - last 5 years | 648 | `b375a0afc138cdea1c295e5f51e4a8d1c13992231d2e6adcf26b6a54c6dd39ea` |
| MSD v1 | Supplementary - last 5 years | 980 | `4c46e531f31c84e83eb481875d5d53996ef7bf035654d6de24fdcdda391038fc` |
