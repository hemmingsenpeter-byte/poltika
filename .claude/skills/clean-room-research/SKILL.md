---
name: clean-room-research
description: Use before reviewing any external policy engine, government-adjacent repository, academic implementation, or third-party model for architectural or capability research — e.g. OpenFisca Aotearoa, PolicyEngine NZ, BetterRules, or any other prior-art system. Governs how that inspection is allowed to happen so it never becomes the source of a Poltika policy value, formula, or rule.
---

# Clean-room research

Poltika's IP Doctrine (BUILD_PLAN.md, doctrine/ip-doctrine.md, ADR-0001) treats
external implementations as reference only, never as policy authority. This
skill is the operational version of that rule: it governs *how* to look at an
external system without letting it leak into Poltika's policy logic.

## When this applies

Any time work involves opening, reading, summarizing, or reasoning about:
- OpenFisca Aotearoa or OpenFisca-core
- PolicyEngine NZ (or any PolicyEngine country model)
- The historical BetterRules implementation
- Any other third-party policy engine, calculator, or rules-as-code repository

This includes indirect exposure — reading a blog post, paper, or issue tracker
that describes one of these systems' internals counts too.

## Required sequence

```text
External implementation
        ↓
identify concept/problem (what question is this system answering?)
        ↓
find an authoritative independent NZ source for that same question
        ↓
write a Poltika-native specification from that primary source alone
        ↓
human approval (Pete)
        ↓
independent implementation
```

Do not collapse or reorder these steps. The external system may only ever
inform step 1 (what concept/problem exists) — never steps 2 onward.

## Timing constraint

Check BUILD_PLAN.md's IP Doctrine before starting: as of the current build
plan, external structural inspection is permitted at exactly two points —
Week 0 Task 3 (schema shape only, after Task 2's independent source mapping,
narrow pre-suite exception) and Task 16 (coverage-gap check, strictly after
the relevant test suite is complete). Outside those two windows, don't
initiate external-system research without checking whether the doctrine has
been revised.

## Explicitly prohibited

```text
LLM → invent a formula from memory or training data
OpenFisca (or PolicyEngine, BetterRules) → copy a formula or value
external implementation → translate its code/logic into Poltika code
blog post / secondary summary → treat as an authoritative statutory parameter
```

None of the above may produce a policy.yaml value, a benchmark expectation, a
rate, a threshold, an eligibility rule, or an abatement formula. If an
external system's approach seems useful, name the *category* it suggests
(e.g. "this system models a separate asset-test entity") and then go find
the NZ primary source for that category independently — per
doctrine/ip-doctrine.md's Allowed usage ("structural inspiration, pattern
review, compatibility checks") vs Disallowed usage ("copying statutory logic
without evidence").

## What to record

Any external-system research session should produce, at minimum:
- what was inspected and why (which task/question it was answering)
- what concept/category it suggested, in the abstract
- what independent NZ primary source was then consulted for that concept
- confirmation that no value, formula, or rule was carried over directly

This is the evidence trail the IP Doctrine's "log a one-line ADR confirming
this sequence was followed" requirement expects.
