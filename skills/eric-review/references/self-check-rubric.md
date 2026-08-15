# Formal Sign-Off Self-Check

Use only before returning a FORMAL_SIGNOFF verdict:

- Is the exact frozen identity named?
- Were all mandatory source/render/runtime/playback gates checked against that identity?
- Are observed blockers separated from evidence gaps?
- Is the reviewer independent of the frozen artifact's implementation?
- Are sign-off and publish/send/deploy authority kept separate?

Any open P0/P1 blocks readiness. Missing mandatory evidence is `INSUFFICIENT EVIDENCE`. Missing independence is `PENDING INDEPENDENT REVIEW` when all other mandatory gates pass. No score or checklist total overrides these rules.
