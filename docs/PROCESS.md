# Development Process

Every feature goes through the same 7 phases on its own branch. Claude runs them with `/feature`;
you decide at every gate. This file explains the process; `.claude/commands/feature.md` is what Claude follows.

```
 /start ─► /spec ─► /build ─► /test ─► /review ─► /finalize ─► /ship
 0 Start   1 Spec   2 Build   3 Test   4 Review   5 Finalize   6 Ship
 Gate 0    Gate 1   Gate 2    Gate 3   Gate 4     Gate 5       Gate 6 → PR → you merge
                   (per step)
```

## Phases

| # | Phase | Command | What happens | Output | Gate (you) | Model |
|---|---|---|---|---|---|---|
| 0 | **Start** | `/start` | Check git state; usage snapshot; create `feature/NN-name` from `main`; empty spec | Branch, spec with `Status: draft` | **Gate 0:** paste `/usage` | — |
| 1 | **Spec** | `/spec` | Write the spec: goal, changes, 5 steps, test cases (unit / API / Postman) | Full `docs/specs/NN-name.md` | **Gate 1:** approve spec | Opus (`opusplan`) |
| 2 | **Build** | `/build` | Implement one step at a time with basic tests; Stop hook runs pytest after every turn | Code, basic tests, Postman requests | **Gate 2:** check each step in the browser | Sonnet |
| 3 | **Test** | `/test` | **test-writer** agent adds independent tests from the spec; full pytest; Postman run; failures fixed | Test results + spec coverage map | **Gate 3:** accept results | Sonnet (agent) + tools |
| 4 | **Review** | `/review` | **code-reviewer** agent reviews code AND tests against rules and spec; Must-fix applied | Must / Should fix list | **Gate 4:** choose Should-fix items | Opus (agent) |
| 5 | **Finalize** | `/finalize` | If review changed code: pytest again (+ Postman if endpoints touched). Tick PLAN, update ARCHITECTURE, usage snapshot | Final results, updated docs | **Gate 5:** paste `/usage` | tools |
| 6 | **Ship** | `/ship` | Commit on the branch, push, PR title + description | Pushed branch, PR text | **Gate 6:** confirm commit | Sonnet |

After Gate 6 **you** open the PR on GitHub, review it, merge it, then:
`git switch main` → `git pull` → `git branch -d feature/NN-name` → `/clear`.

## Why this order
- **Spec before code:** fixing a plan is cheap, fixing code is expensive.
- **Test before review:** don't spend review effort on code that doesn't work; the reviewer can also judge the tests.
- **Re-test after review:** review fixes change code; the results in the PR must describe the exact code in the PR.
  Skipped automatically when the review changed nothing.

## Test levels
| Level | Folder | What it tests | Runs |
|---|---|---|---|
| **Unit** | `tests/unit/` | Pure functions in `app/rules/` (slots, overlaps, status changes). No Flask, no DB. | Stop hook (every turn), Phase 3, Phase 5 |
| **API** | `tests/api/` | Endpoints through Flask's test client with a temporary DB and fixed clock | Stop hook, Phase 3, Phase 5 |
| **Postman** | `postman/` | The real server over HTTP: full flows, cookies, roles | Phase 3; Phase 5 if endpoints changed |

Who writes them:
- **Builder** (main session, Phase 2): basic tests per step so the Stop hook catches breakage early.
- **test-writer** agent (Phase 3): tests for every spec test case, derived from the spec, not from the code.

## Models
| Who | Set where | Model |
|---|---|---|
| Main session | `/model opusplan` before `/feature` | Opus while planning, Sonnet while building |
| test-writer agent | `.claude/agents/test-writer.md` | Sonnet |
| code-reviewer agent | `.claude/agents/code-reviewer.md` | Opus |
| Searches | built-in Explore agent | (default) |
If Opus reviews use too much of your weekly limit, set the reviewer to `sonnet` and keep Opus for
features that touch booking, time rules or roles.

## Safety
- **Deny rules** in `.claude/settings.json`: no force-push, push to `main`, merge, `reset --hard`,
  `git clean`, `--no-verify`, or reading `.env` / databases.
- **Stop hook**: pytest after every turn that changed Python files; failures go back to Claude.
- **Format hook**: `ruff format` after every edit.
- **commit-msg git hook** (`.githooks/commit-msg`): removes AI co-author and "Generated with" lines.
- **Stop conditions** in `/feature`: 3 failed fix attempts, work outside the spec, unclear reply → stop and ask.

## Commands
Run the phases one by one while learning; switch to `/feature` once you know the flow.
Each command checks the spec's `Status:` first and ends by naming the next command.

| Command | Phase | Requires spec status | Sets status |
|---|---|---|---|
| `/start [NN or description]` | 0 Start | (no open feature) | `draft` |
| `/spec` | 1 Spec | `draft` | `approved` |
| `/build` | 2 Build | `approved` or `building` | `building` → `built` |
| `/test` | 3 Test | `built` | `tested` |
| `/review` | 4 Review | `tested` | `reviewed` |
| `/finalize` | 5 Finalize | `reviewed` | `done` |
| `/ship` | 6 Ship | `done` | (commit + push) |
| `/feature [NN or description]` | 0–6 | (same checks) | all of the above |

The current feature is the spec whose `Branch:` line matches the current git branch, so every command
works after `/clear` or in a new session.

## Tracing what each phase changed
- After each command: VS Code Source Control panel, or `git status` and `git diff --stat`.
- Optional checkpoint commit between phases (you run it): `git add -A` then `git commit -m "wip: phase 2 build"`.
  Merge the PR with "Squash and merge" so `main` gets one commit per feature.
- `/context` after each phase shows how much context the phase used.

## Measuring AI usage
Gate 0 and Gate 5 record `/usage` before and after. Results go into the spec (`## AI usage`)
and `docs/AI_USAGE.md`. Don't use claude.ai chat while a feature is being measured.
