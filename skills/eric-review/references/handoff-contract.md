# Review-to-Fix Boundary

Use this only when Eric asked for REVIEW_AND_FIX or separately authorized a repair after QUICK_REVIEW.

1. Bind the fix to the named artifact and concrete finding.
2. Edit the smallest relevant surface and preserve unrelated work.
3. Run one recheck that can prove or disprove the fix.
4. Report the changed identity, result, and any remaining issue.

Do not require an audit checkpoint, handoff packet, another writer, or return packet for an ordinary same-agent repair. Stop only when the fix changes product intent, expands materially beyond the named artifact, incurs cost, requires external authority, or would overwrite accepted work.

For FORMAL_SIGNOFF, any mutation creates a new identity and invalidates the sign-off attempt. Finish repairs first, freeze again, then use the single allowed independent review. Sign-off never authorizes publish, deploy, upload, send, migration, or destructive execution.
