# Bounded repair state machine

At Q1+, preserve each failed gate before editing:

```json
{"finding_id":"F-001","gate_id":"G-TEST-001","artifact_identity":"hash/version","command_or_probe":"exact command","exit_code_or_status":"1","failure_signature":"normalized broken criterion","first_observed_at":"ISO-8601","attempt_count":1,"hypothesis":"one falsifiable cause","evidence_for_hypothesis":["path:line/log/screenshot"],"change_since_previous_attempt":["exact files or none"],"new_root_cause_evidence":[]}
```

## Transitions

1. First failure: preserve output, isolate the smallest surface, form one falsifiable hypothesis, and add/refine a reproducer when possible.
2. First repair: change only files supported by that hypothesis; rerun the targeted gate.
3. Same fingerprint again: stop implementation edits and follow this state machine directly. Record the blocked repair state, then inspect assumptions, paths, logs, environment, data grain, render pipeline, or source identity before proposing another hypothesis.
4. Materially new root-cause evidence permits one second implementation attempt with an updated hypothesis.
5. Failure after attempt two: return `BLOCKED_REPAIR_BUDGET`. A third change requires both Eric approval and a materially new root cause.
6. Use a new finding ID only for a different underlying criterion.
7. After repair succeeds, run the broader relevant suite and inspect the actual target surface.

Normalize a fingerprint as `gate_id + failure_signature + criterion/finding_id` after trimming, lowercasing, and collapsing whitespace. Attempts after one require a non-empty stable `criterion`, complete preceding records, and exactly contiguous counters beginning at one; changing a finding ID does not reset or truncate the history. Repeated normalized fingerprints must appear in strictly increasing timestamp and attempt order. A repeated fingerprint cannot return to `repair` unless `new_root_cause_evidence` adds at least one normalized locator not already recorded as hypothesis or root-cause evidence for that group—otherwise switch to diagnosis.

Every fingerprint value is semantic, not merely present: identifiers, command/probe, signature, hypothesis, and artifact identity are non-empty; `first_observed_at` is an ISO-8601 date-time with timezone; attempt count is a positive integer; hypothesis evidence and change history are non-empty string lists; new-root-cause evidence is a string list that may be empty. Attempt three requires both materially new evidence and an explicit positive Eric authorization in the structured form `{"status":"granted","by":"Eric"}` (the equivalent positive statuses `approved` and `authorized` are accepted). Free-form strings, denied, pending, non-Eric, arbitrary, or merely truthy values never count.

## Red flags and rationalizations

Stop if anyone proposes “one more quick patch”, reruns unchanged commands as diagnosis, changes unrelated layers under one hypothesis, weakens the test, renames the same defect, or treats a timestamp/new filename/generic pass as proof. Deadline, sunk cost, confidence, validator success, and implementer assurance never replace required evidence.
