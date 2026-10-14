---
description: Phase 2 Build. Implement the approved spec step by step, with a manual check after each step
---

Run **Phase 2 (Build)** of `.claude/commands/feature.md` for the feature on the current branch,
including **Gate 2** after every step.

Before starting, check (see "Finding the feature" in feature.md):
- Not on `main`, and the spec has `Status: approved` or `building`. Otherwise stop and tell me which command to run first.
- If some steps are already marked ✅, continue from the first step that is not.

Stop after the last step's Gate 2. Do not start testing. Then show me:
- `Status: built`
- **Next command:** `/test`
