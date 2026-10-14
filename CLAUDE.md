# Clinic Booking

Appointment booking for one small clinic. A receptionist finds or registers a patient,
picks a doctor, a date and a free slot, and books it. Doctors see their schedule and mark
each visit completed or no-show. Admin sees reports. Learning project: keep everything simple.

## Stack
- Backend: Python 3.11+, Flask, SQLite via the built-in `sqlite3` module (no ORM)
- Frontend: plain HTML, CSS and JavaScript served by Flask (no frameworks, no build step)
- Tests: pytest (unit + API), Postman collection run with Newman. Formatting: ruff.
- Package manager: uv. Dependencies live in `pyproject.toml` (locked in `uv.lock`).

## Commands (run from the project root)
- Install:      `uv sync`
- Init DB:      `uv run flask --app app init-db`
- Seed:         `uv run flask --app app seed`
- Run:          `uv run flask --app app run --debug`  → http://127.0.0.1:5000
- All tests:    `uv run pytest -q`
- Unit only:    `uv run pytest -q tests/unit`
- API only:     `uv run pytest -q tests/api`
- Postman:      `uv run python scripts/postman_run.py`  (fresh DB, own server on port 5001, Newman, summary)
- Format:       `uv run ruff format .`
- Reset DB after a schema change: delete the database file in `instance/`, then run init-db and seed again

Always prefix Python tools with `uv run`. Never use `pip install`.

## Layout
- `app/`          Python backend: endpoints → handlers → services → repositories, plus pure `rules/` (see `app/CLAUDE.md`)
- `frontend/`     HTML pages, CSS, JS (see `frontend/CLAUDE.md`)
- `tests/unit/`   unit tests for `app/rules/` (no Flask, no DB)
- `tests/api/`    API tests through Flask's test client (temporary DB, fixed clock)
- `postman/`      Postman collection + environment (a request for every endpoint)
- `scripts/`      developer tools (`postman_run.py`)
- `.githooks/`    git hooks (`commit-msg`)
- `instance/`     SQLite database files (git-ignored)

## Docs
- `docs/PROCESS.md`       the 7-phase feature pipeline and its gates
- `docs/PLAN.md`          features in build order + out of scope. Read before starting a feature.
- `docs/ARCHITECTURE.md`  data model, time rules, slot rules, status changes, API, pages
- `docs/specs/`           one spec per feature (`NN-short-name.md`), created in Phase 1
- `docs/AI_USAGE.md`      tokens and plan usage per feature

## Time rules (important)
- The clinic has one time zone: `CLINIC_TZ` (default `Asia/Karachi`).
- Appointment times are stored as clinic-local strings `YYYY-MM-DDTHH:MM` (no offset).
- Get "now" only from `app/clock.py` (`now()`), never `datetime.now()` directly, so tests can fix the time.
- Weekdays use Python's numbering: Monday = 0 … Sunday = 6.

## Testing rules
- Every spec test case must map to at least one test (unit, API or Postman).
- Time and slot logic lives in pure functions in `app/rules/` and is unit-tested with explicit inputs.
- Time-based tests always fix the clock; never depend on the real date.
- Fix the code, not the test, unless the test contradicts the spec. If you change a test, say why.
- Test file names must be unique across `tests/unit/` and `tests/api/` (pytest imports them by name).
- Name tests after the spec case ID when there is one, e.g. `test_A3_book_without_login_returns_401`.

## Conventions
- Every API response: `{"status": true|false, "message": "...", "data": ..., "errors": []}`
- Secrets and config come from environment variables with a dev-only fallback
  (`SECRET_KEY`, `CLINIC_TZ`, `CLINIC_DATABASE`).
- Files `{entity}_{layer}.py` (e.g. `appointment_service.py`); pure rules `{topic}_rules.py`.
  Functions `verb_noun`. Type hints everywhere.
- Use `logging`, not `print()`.

## Rules
- Build only what the current spec asks for. Check "Out of scope" in `docs/PLAN.md`.
- Do not add dependencies or JavaScript libraries without asking. If approved, add with `uv add`.
- Only change files needed for the task.
- Never read or edit `.env`. Never run `git clean`.

## Git
- Never commit to `main`. Each feature gets its own branch: `feature/NN-short-name` (NN = plan item).
- Start every branch from an up-to-date `main`.
- Commit only on the feature branch, after I confirm the message. Never use `--no-verify`.
- Never add `Co-Authored-By`, "Generated with Claude Code" or any AI attribution to commits or PR text.
