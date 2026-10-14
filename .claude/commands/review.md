---
description: Phase 4 Review. Code-reviewer agent on all changes on this branch; apply Must fix and chosen Should fix items
---

Run **Phase 4 (Review)** of `.claude/commands/feature.md` for the feature on the current branch, including **Gate 4**.

Before starting, check (see "Finding the feature" in feature.md):
- Not on `main`, and the spec has `Status: tested` (or `reviewed`, in which case ask whether to review again).
  Otherwise stop and tell me which command to run first.

After applying my choices, stop and show me:
- whether Phase 4 changed any code (yes/no, which files)
- `Status: reviewed`
- **Next command:** `/finalize`
