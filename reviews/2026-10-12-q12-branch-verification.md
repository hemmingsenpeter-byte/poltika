# Q12 branch deletion: verified list, 12 October 2026

Pete approved deleting the merged remote branches on 12 October 2026
([record](../docs/programme/2026-10-12-pete-approvals.md), Q12). Claude Code
checked the list against `origin` that day, re-checked that no tip had moved,
and deleted all 91 branches on 12 October with the command below.

- **87 branches from the 7 October list** (`reviews/2026-10-07-closeout.md`):
  every tip still equals `refs/pull/N/head` of its squash-merged PR, so each PR
  keeps the commit.
- **4 branches added on 12 October**:
  - `fix/v1-scenarios-validationerror-20261012` and
    `test/wff-as-boundary-proposal-20261012` reverse-apply cleanly on `main`;
  - `test/followups-20261012` and `fix/web-a11y-targets-20261012` were
    cherry-picked into #211. They differ from `main` only where later commits
    edited the same files.

  These four have no PR head, so the tips below are their only remote
  record.
- **`feat/b016-responsive-20261011`** was already deleted when #209 merged.

The command that deleted them, run from a checkout:

```sh
git fetch --prune origin
git push origin --delete $(awk '/^[0-9a-f]{40} /{print $2}' reviews/2026-10-12-q12-branch-verification.md)
```

To restore any one of them: `git push origin <sha>:refs/heads/<branch>`.

## Tips at verification (SHA, branch)

```text
1edd9e814422905c83accc6a08d72254b8260a70 adr/delegated-acceptance
52efd0e470ffd0c41656bb713e333bede5f919a1 ci/test-workflow
fe57d39650b189710af6911e18dc2346173921db claude/decision-instrument-plan
1bce7ed810e2fcfcbf6d48da3650dd4589be40d9 claude/funny-ptolemy-9osdml
dc1e91ad899bc00422d9f524b516a9fc31507114 claude/relaxed-noether-azyj77
5996ccc1830955fb931cf09edd6518ba1ea32a9e claude/render-connector-verify-ur97hc
2404ab47fc17b5c685382155cf616e5b014e92ee codex/pr128-review-closeout
ea872403acdd3e3a37a15040161d4fb847332f12 codex/pr128-review-fixes
0d8e1a2af4d675b5e09ec8af26a526ab01bd60af copilot/finish-installed-artifact-test
ee75b12cacf964363c266809fcac7eec237c1ce0 data/v0-2-cross-validation
ef5c2f02572ca0950b096909e5baaa4e6d5cfe2f data/v0-2-real-population
4f9c1f301f1ec0d5f20a8b1af8bf9772cddfa8cc data/v0-2-task-3-2-snapshots
b89a3536009f5020096eff7b5aab7d1d08ae7d68 docs/agent-instructions-render
0986f36ce60c81de458cfc242d0f6b6039b77961 docs/as-rate-contract-resolution
ad79e0fed02c42b8cce80ff1749cd97825d95ccf docs/constitution-decisions
05710085fae188da5777a9c9ae7c509f3771202b docs/epistemic-constitution
86d9df718f234cd1efc91614f0c738f8408efd5a docs/governance-files
1cb80fec4b3bd49cddf754fbe6d8052a1bd47ed6 docs/legislation-currency-check
d91983a3f6505fc5cf71840d7e2b9f8c1b143b86 docs/orientation-doc
911ffad597c45926e358f7ee7a2f854c74fa2702 docs/programme-adr-archive
7434cec604d124437b5c02e3a32fb8cbdc2354bc docs/programme-status
c388b64e549a0f276c42418a0e03d394648cd61b docs/readme-status
bd97f227a0b36e0acf3db5f8b3149ca37875614f docs/reconcile-live-status-2026-10-03
155cc8d6647ab35cc13acc5c08f6894b5c3cd937 docs/record-26a-28-status
1f2159fb732c3df407871ec52a22e9945c3e2467 docs/record-26a-complete
8ead294c407b0b082921b9f2926438bd8ce0b020 docs/record-27-31-32-status
fb9b8f9d8ea650980ef848187e6c76c4d15bd121 docs/record-task24-8-26-acceptance
3c3a13ba31ba1d9fe448337e894403611cdc4add docs/record-task28-complete
d890bd4bd0196d48aad67d5a2c6ccebfaffe34c0 docs/session-orientation-plan
33ad601c1d2c93156dfa5a91aa3cb4cbec466bbf docs/status-32-34
b7ae5796489b40c9877e4640918d8ec300206ebf docs/task-10-wff-spec-draft
81feb92834a2dbb13802c7d2ce5627e0bdc8e966 docs/task10-closure-first
fe40ffb8102a700ddffdc9e66e54bb702c98741c docs/task10-final-source-audit
d9cc27fcf7431b898335fca37dfdf1369c389c02 docs/task10-mb-mc-final
bf70d1bdb911a8cb2e57d04f58b183e9d155edfd docs/task10-temp-iwtc-rate
d289323bd79452cc1ef33d6751d2444cd1ad1a20 docs/task10-wff-approval
679d33134aafdc7942ee63cc2ab46e749f72c5e8 docs/task17-review-packet
794b9a60e189d1857d482d3934e786ad5862e391 docs/task24-3-as-coverage-gap
128fc1acafdb1dcf9596c120cd9a69bb80a8262e docs/task26a-as-rates
5389f52b11b2bb4341ffe2ee0d643207ed778d06 docs/task26b-order-check
b9da050ab82358b52bd9e3d294ac5eb7b3db2d6e docs/task27-2-schema-md
927ec894fc68cdd46c26acaaafdec76228d416cf docs/task28-1-interaction-sources
d6eb851576a87dcf6e1ab69e42cae437dfd538e2 docs/task28-2-period-research
d31752dc06f08ee1a5158a84a14c489a6ffcdca3 docs/task28-3-interaction-contract
d81a37c0ff31a44ee6641a79c07a5198b3fc1447 docs/task32-1-storage-adr
eb6d5fcb2ed8f37ac73b56fd2dc271f317035240 docs/task34-4-codex
b0a9abac7a58040006e3e07d2fb82b55b97af185 docs/task35-demo
5f58659fcfd14826862fb2b2fefa886337e3c106 docs/v0-1-question-set
84eb4616f5d5521f90f1606e01222fb19116dba2 docs/v0-2-audit-packet
ea64303999c0ab5a2eb1b57f8b0fdd6c95284d41 docs/v0-2-status
f7a65cec836298a354c3f8cbaf6115b61712daa8 docs/v01-plan-refinement
4eccaae6ac00508d0d9ad5b1320721cd0cb94d1c feat/as-rate-selector-repair
abc0d2dc15ad9538c5a99c46932c6bef68410ed1 feat/provenance-structured-check-dates
7aec12385e13047d029adc62ee7ca3e8daeacfc1 feat/task26a2-as-rate-values
98d3ef4a3c2044732eec5c5bcae54a3f7290de90 feat/task28-4-combined-runner
1968c331d9e0f83e7b5e7712db7b31e3bddae06b feat/task28-5-interaction-cases
b2116bb387f0feac90cde9442b07cb6ab04de76b feat/task29-golden-households
c933b9156b9050c37eeca2f116d37d090646473e feat/task30-deterministic-scenarios
40764b9d447f737bba6a84e73213d4c03fdd8fe5 feat/task31-6-combined-provenance
d3ed5d4c0600847e5beae68c1178ae99464f0379 feat/task31-provenance-trace
4361a4e5deed81772cd9a7963b15c11ac29e3495 feat/task32-postgres-store
a9b7cd127b3342a07f7719886dbe6005d6e3c6a1 feat/task33-2-scenario-routes
c214c9f7bb69878c93f3b4a30464243cda718da3 feat/task33-household-api
f903b9e64e53bba79248f8d73c59ecd9a681cb68 feat/task34-acceptance
fe314a958216937e69a930028bd9295c69ac809f fix/as-weekly-validation
8314907a39c0077025575f320c52743621e7cfd1 fix/hosted-hardening
c5d4ea25dfa0448681be53372e2f4f96dd883efb fix/q71-140-review
9909fd5535d7faed43727c512178e76bf7415b58 fix/task34-4-review-fixes
7be059d6ac3ef264c64025846c2303faa5ef6264 fix/task34-4-review-fixes-2
1390946595a84162a85b1e44ecd750f1891a0a61 fix/v0-2-fresh-check
83db26dd92b99925f7641725c33dce042fe44ef5 fix/v0-2-transformation-versions
d952e0bc7653f3aef5c6a1d40f3d693e475e3514 infra/security-ci
9fca1d8831435c110d7a65bb5d4a4bb4b9dcba64 prog/evidence-classes-skill
a1cdb5fb1c1a33b7b28837ee3cd265a53c2a2d09 review/pr109-fixes
8d7e7b122750fd4e11021380b61894512a9fabe6 review/pr122-127
6fa3424fc6ea582227f79f07f159fd3175f04e79 review/queued-pr-audit
0d9d20556c749b39613328db3a8ef070ecbac1dc review/v02-release-evidence
a11f726ca4aabb7116fc3e0841d7d30627d2037a task24-2-as-regressions
5ffc1aa6994f326e97c8d97e626ec3127f54280e task24-4-as-review
1d8bf8716bd2340a1af6e03ac4defadb2a825eca task24-6-as-review-fixes
0186766387673251302568dff49dd2f467043c11 task24-7-as-module
79441c2a90e48f6406ca20508ec9ac3e77b47de5 task24-8-as-api-route
0666be4ade4642ddc4f275a674e52e3fa990470f task26-as-base-rate-compound-id
2ba1b7e0e68461a17b25f61372943418a31e261d test/as-installed-artifact
c3c053a434cdb25266070775fd061b25a376d183 test/conftest-mypy-strict
340fd2bb8dcc92f9eaebc88d18c435fef5509082 test/v0-1-acceptance-suite
e843cf84e15b3f0e9ed5f7193c169cb73426a803 test/v0-2-hand-calculated
1ff664404fb0c911eee5a8e837b0813bb6891196 test/followups-20261012
7f7d772a8e1bd3b1b9573747f68ac096f60e21ba fix/web-a11y-targets-20261012
714d0caad978da81eb0cba97d3c2b4c50486c49d test/wff-as-boundary-proposal-20261012
29db419fc4eb39eec03b052d0ec7700c6b536cda fix/v1-scenarios-validationerror-20261012
```
