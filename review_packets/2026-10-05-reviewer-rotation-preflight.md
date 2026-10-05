# ADR-0020 reviewer rotation — author preflight

Date: 5 October 2026. Author: GPT/Codex.
Base: 1e185f7652bebce693a9c709cb716b4a9bcfdf5a.
First fixed implementation head: 98314e5. Final review must name the published
head after this evidence packet is added. This author preflight cannot clear
the independent reviewer gate.

Expected contract: preserve BUILD_PLAN's other-model rotation, all Tier C
boundaries, final-head author preflight and fresh-context reviewer passes,
latest-head green CI, current main and squash merging. Codex authorship needs
Claude review; Claude authorship needs GPT/Codex review. A same-model pass must
never clear the cross-model row. Existing review comments predating branch
updates cannot stand for a new head.

No blocking author finding. Entry points, ADR, review doctrine, development
wording and reviewer skill agree on the rotation and final-head rule.
Project permission settings remain an uncommitted proposal pending Pete's
explicit approval of their command and branch scope. This PR changes no tool
permissions, protected values, policy logic, production module or data snapshot.

Isolated author preflight: programme-authority and review-queue tests pass
(12 tests); offline Markdown links/fragments and git diff check pass.
The amendment is authorised by Pete's supplied item 4 and closeout request.
A new temporary Tier C waiver is not inferred. Final-head cross-model Claude
review and required CI are pending separate gates.
