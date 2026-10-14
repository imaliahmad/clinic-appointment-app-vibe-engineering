# AI usage per feature

Fill in one row per feature (Gate 5 of `/feature` reminds you).
Weekly % / Session % come from `/usage` before and after the feature.
Tokens come from `npx ccusage@latest session` (or your own tracker).
Avoid using claude.ai chat while a feature is being measured.

| # | Feature | Size (S/M/L) | Model(s) | Tokens | Session % used | Weekly % used | Fix rounds (Gate 2) | Bugs found in Test / Review | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 01 | Skeleton | S | Opus 5.5 (main), Sonnet (test-writer), Opus (code-reviewer) | not recorded | n/a (window reset; 12 → 10) | 2 (16 → 18) | 0 | Test: 0 bugs · Review: 1 must fix (missing type hint) | 1 spec change during build: pytest `pythonpath` in `pyproject.toml` |
| 02 | Seed | S | Opus 5.5 (main), Sonnet (test-writer), Opus (code-reviewer) | not recorded (agents ~24k + ~29k) | 7 (12 → 19) | 1 (18 → 19) | 0 | Test: 0 bugs · Review: 0 must fix, 8 should fix (all skipped) | 4 steps instead of 5; no spec changes during build |
| 03 | Login & roles | M | Opus 5.5 (spec), Sonnet 5.5 (build), Sonnet (test-writer), Opus (code-reviewer) | not recorded (agents ~30k + ~42k) | 6 (21 → 27) | 1 (19 → 20) | 1 (step 4: 401 on login, dev DB was not seeded; no code change) | Test: 0 bugs · Review: 0 must fix, 8 should fix (all skipped) | 5 steps; static route and ARCHITECTURE line added beyond the spec's Changes list |
