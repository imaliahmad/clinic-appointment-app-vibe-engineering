---
description: Phase 5 Finalize. Re-test if review changed code, update PLAN/ARCHITECTURE, record usage after
---

Run **Phase 5 (Finalize)** of `.claude/commands/feature.md` for the feature on the current branch,
including **Gate 5**.

Before starting, check (see "Finding the feature" in feature.md):
- Not on `main`, and the spec has `Status: reviewed`. Otherwise stop and tell me which command to run first.
- The re-test decision comes from the spec's `## Review summary` ("Code changed in review: yes/no").
  If that line is missing, treat it as "yes".

When done, stop and show me:
- final test results (unit / API / Postman, or "re-test skipped: no changes")
- `Status: done`
- **Next command:** `/ship`
