---
description: Run the full feature pipeline (start → spec → build → test → review → finalize → ship) with approval gates
argument-hint: "[feature number or description]"
---

# Feature pipeline

Feature: $ARGUMENTS. If empty, use the first unticked item in `docs/PLAN.md`.
The process is described in `docs/PROCESS.md`. This file is the exact procedure. The single-phase commands
(`/start`, `/spec`, `/build`, `/test`, `/review`, `/finalize`, `/ship`) each run one phase of this file.

Work through Phases 0–6 in order. At every **GATE**, stop completely and wait for my reply.
Never skip a gate, never combine two gates in one message, even if everything looks fine.

## How to read my replies at a gate
- `ok`, `yes`, `continue`, `approved` → go on.
- `stop` → stop work, summarize where we are (phase, step, branch, uncommitted files), and wait.
- Anything else → a change request or bug report. Fix it, run `uv run pytest -q`,
  then show the same gate again. Do not move on until I reply `ok`.

## Finding the feature
The current feature is the spec in `docs/specs/` whose `Branch:` line equals `git branch --show-current`.
Its `Status:` line says which phase is complete:

| Status | Set when | Next phase |
|---|---|---|
| `draft` | Phase 0 done (branch + empty spec) | 1 Spec |
| `approved` | Gate 1 approved | 2 Build |
| `building` | Phase 2 in progress (steps marked ✅ as they finish) | 2 Build (continue) |
| `built` | last Gate 2 accepted | 3 Test |
| `tested` | Gate 3 accepted | 4 Review |
| `reviewed` | Gate 4 decisions applied | 5 Finalize |
| `done` | Phase 5 complete | 6 Ship |

A phase only starts if the spec has the status in the "Next phase" column for it.
If not, stop and tell me which command to run first. Update `Status:` the moment a phase completes.

---

## Phase 0: Start

1. Run `git status` and `git branch --show-current`.
2. Uncommitted changes → stop and list them. Wait for my decision.
3. Already on a `feature/...` branch with a spec that is not `done` → tell me its status (and step)
   and the command that continues it. Stop.
4. Otherwise: `git switch main`, `git pull`, `git switch -c feature/NN-short-name`
   (NN = plan item number, two digits).

### GATE 0: Usage before
Ask me to run `/usage` and paste the session % and weekly %.

5. Create `docs/specs/NN-short-name.md` from `docs/specs/_TEMPLATE.md` with only the header filled
   (title, `Status: draft`, `Plan item:`, `Branch:`) and the Gate 0 numbers in the "Before" row of `## AI usage`.

---

## Phase 1: Spec

1. Read `docs/PLAN.md`, `docs/ARCHITECTURE.md`, `docs/PROCESS.md`, and only the existing files this feature touches.
2. Fill in every section of the spec:
   - **Goal:** 1–2 sentences.
   - **Changes:** every file to create or change, one line each.
   - **Steps:** **5 steps**, each small, building on the previous one, leaving the app runnable.
     Each step has `Build:` and `Check:` (exact manual test: URL or command, what to do, expected result).
     If 5 steps would be artificial, propose fewer and say why.
   - **Test cases** with IDs:
     - Unit (U1, U2, …) for every pure rule, including boundaries
     - API (A1, A2, …): happy path, bad input (400), not logged in (401), wrong role (403), conflicts (409)
     - Postman (P1, P2, …): the requests this feature adds
   - **Out of scope:** what this feature won't do (check `docs/PLAN.md`).
3. Do not write or change any code in this phase.

### GATE 1: Spec approval
Show me the branch name and the full spec.
Ask: **"Approve this spec? Reply `approved` or tell me what to change."**
On approval: `Status: approved`.

---

## Phase 2: Build

1. Set `Status: building`.
2. For each step in `## Steps` not yet marked ✅, in order:
   1. Announce **"Step X of N: <name>"**.
   2. Implement only that step's `Build:` line. Follow `CLAUDE.md`, `app/CLAUDE.md`, `frontend/CLAUDE.md`,
      and the `add-endpoint` skill for every API endpoint (including its Postman request).
   3. Add basic tests for what this step makes testable (pure rules → `tests/unit/`, endpoints → `tests/api/`).
   4. Run `uv run pytest -q`. Fix the code until it passes. Same failure after 3 attempts → stop and report.
   5. Mark the step done in the spec (`1. ✅ …`).

### GATE 2 (after every step): Manual check
Show me:
- **Done:** 2–4 bullets
- **Files changed:** list
- **Tests:** `uv run pytest -q` result
- **Please test:** the step's `Check:` as numbered actions, with the command to start the app
  (`uv run flask --app app run --debug`) and the URL
Ask: **"Step X works? Reply `ok` to continue, or describe the problem."**
Problem → reproduce from my description, fix, run tests, show Gate 2 for the same step again.
After the last step's `ok`: `Status: built`.

---

## Phase 3: Test

1. Use the **test-writer** agent. Give it the spec path. It adds tests for every case ID and reports:
   coverage map, results, failing tests, spec gaps.
2. Run all tests yourself: `uv run pytest -q tests/unit`, `uv run pytest -q tests/api`.
3. If this feature added or changed endpoints: run `uv run python scripts/postman_run.py`.
4. For every failure: fix the **code** (not the test, unless the test contradicts the spec; then say why),
   and run the failing level again. Same failure after 3 attempts → stop and report.
5. Fill the spec's `## Test results` (results, coverage map, spec gaps).

### GATE 3: Test results
Show me:
- **Unit:** X passed · **API:** Y passed · **Postman:** N requests, M assertions passed (or "no endpoint changes")
- **Coverage:** every case ID → test name; any case without a test
- **Fixed during testing:** bugs the tests found and what you changed
- **Spec gaps:** from the test-writer, each with your suggestion
Ask: **"Accept the test results? Reply `ok`, or tell me what to change (e.g. decide a spec gap)."**
If I decide a spec gap: update the spec, add the test, fix the code, and show Gate 3 again.
On `ok`: `Status: tested`.

---

## Phase 4: Review

1. Use the **code-reviewer** agent on all changes on this branch vs `main` (committed and uncommitted, code and tests).
2. Fix every **Must fix** item and run `uv run pytest -q`. If one needs a change outside the spec, don't fix it;
   list it for Gate 4.

### GATE 4: Review decisions
Show me:
- **Must fix:** each item and what you changed (or "none")
- **Should fix:** numbered; each with file:line, problem (one line), your recommendation (**fix** / **skip**) and why
- **Looks good:** short list
Ask: **"Which Should fix items should I apply? Reply with numbers (e.g. `1, 3`), `all`, or `none`."**
Apply only what I choose and run `uv run pytest -q`. Write the spec's `## Review summary`,
including **"Code changed in review: yes/no"** and the files. Then `Status: reviewed`.

---

## Phase 5: Finalize (re-test & docs)

### 5.1 Re-test
- If the Review summary says "Code changed in review: no" → write "re-test skipped: no changes" in `## Test results`.
- Otherwise run `uv run pytest -q`, and if a changed file is in `app/endpoints`, `app/handlers`, `app/services`,
  `app/repositories` or `app/rules`, also `uv run python scripts/postman_run.py`.
  Any failure → fix, re-run, tell me what broke. Update `## Test results` with the final numbers.

### 5.2 Docs
1. Tick the feature in `docs/PLAN.md`.
2. Update `docs/ARCHITECTURE.md` if tables, endpoints, pages or rules changed (or say nothing changed).

### GATE 5: Usage after
Ask me to run `/usage` and paste the session % and weekly %, and (optional) the token count from
`npx ccusage@latest session`. Fill the spec's `## AI usage` ("After", "Used", models) and add a row to
`docs/AI_USAGE.md` (including fix rounds at Gate 2 and bugs found in Phases 3–4).
Then `Status: done`.

---

## Phase 6: Ship

1. `git branch --show-current` must not be `main`; if it is, stop.
2. `uv run pytest -q` one last time.

### GATE 6: Commit
Show me `git status` and the commit message: title `Feature NN: <name>` + 3–5 bullets.
No `Co-Authored-By`, no "Generated with" line, no AI attribution.
Ask: **"Commit and push this? Reply `yes`, or tell me what to change."**

### After `yes`
1. Commit on the feature branch (never with `--no-verify`).
2. `git push -u origin feature/NN-short-name`.
3. Give me, ready to paste into GitHub (no AI attribution lines):
   - **PR title**
   - **PR description** (markdown): what changed; how to test manually (from the steps' Check lines);
     test results (unit / API / Postman); review summary; AI usage
4. Remind me:
   - Open the PR (base `main` ← `feature/NN-short-name`), review it, and merge it yourself
     (use "Squash and merge" if the branch has WIP commits).
   - Then `git switch main`, `git pull`, `git branch -d feature/NN-short-name`, and `/clear`.

---

## Stop immediately and report if
- The same failure survives 3 fix attempts
- The work needs a file or change that is not in the approved spec
- Any action would commit to `main`, merge, force-push, reset, delete a branch, or skip git hooks
- The spec's status doesn't allow the phase you were asked to run
- My reply is unclear: ask, don't guess

## Never
Merge pull requests, push to `main`, force-push, use `--no-verify`, skip a gate, weaken a test to make it pass,
or start the next phase without my `ok`.
