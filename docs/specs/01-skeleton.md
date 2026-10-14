# Skeleton
Status: done
Plan item: 1
Branch: feature/01-skeleton

## Goal
A developer can install, create the database with `init-db`, run the app and open `/`.
The shared foundations (config, clock, JSON envelope, DB connection, full schema, API test fixtures,
Postman runner) are in place for every later feature.

## Changes
- `app/__init__.py`: `create_app(test_config=None)` app factory: loads config, makes `instance/`, registers
  the page blueprint, the DB teardown, the CLI commands (`init-db`, `seed`) and a JSON 404 handler for `/api/...` paths
- `app/config.py`: reads `SECRET_KEY` (default `dev`), `CLINIC_TZ` (default `Asia/Karachi`),
  `CLINIC_DATABASE` (default `instance/clinic.db`) from the environment; `get_clinic_tz() -> str`
- `app/clock.py`: `now() -> datetime`: current clinic-local time as a **naive** datetime (no tzinfo),
  using `zoneinfo` and `CLINIC_TZ`. The only place that reads the real clock. Works without an app context.
- `app/responses.py`: `success(data=None, message="OK", status_code=200)` and
  `failure(message, errors=None, status_code=400)` returning `(Response, code)` with the envelope
  `{"status", "message", "data", "errors"}`
- `app/db.py`: `get_db()` (one `sqlite3` connection per request, `row_factory = sqlite3.Row`,
  `PRAGMA foreign_keys = ON`), `close_db()`, `init_db()`, `init-db` CLI command
- `app/schema.sql`: all 5 tables from ARCHITECTURE (`users`, `doctors`, `doctor_hours`, `patients`, `appointments`)
  with `CREATE TABLE IF NOT EXISTS`, foreign keys, CHECK constraints (role, slot_minutes, weekday 0–6,
  appointment status), unique (doctor_id, weekday), unique phone, unique username, and the
  partial unique index `appointments(doctor_id, start_at) WHERE status != 'cancelled'`
- `app/seed.py`: placeholder `seed` CLI command that only logs "nothing to seed yet" (needed because
  `scripts/postman_run.py` calls `seed`; feature 2 replaces the body)
- `app/endpoints/page_endpoints.py`: blueprint with `GET /` serving `frontend/login.html`
- `frontend/login.html`: placeholder page: title "Clinic Booking", one line "Login comes in feature 3"
- `tests/api/conftest.py`: fixtures `app` (temporary DB file per test, `init_db()` already run, `TESTING=True`),
  `client`, `runner` (CLI runner), `fixed_now` (monkeypatches `app.clock.now` to return
  `2026-01-05 09:00`, a Monday; returns that datetime)
- `tests/api/test_app.py`: page, envelope and 404 tests
- `tests/api/test_db.py`: schema, index and init-db tests
- `tests/api/test_clock.py`: clock and config tests
- `postman/clinic.postman_collection.json`: add "Unknown API path returns JSON 404" to `00 Health`
- `pyproject.toml`: pytest config `pythonpath = ["."]`, `testpaths = ["tests"]` so tests can import `app`
  (added during Step 1, approved)
- `docs/ARCHITECTURE.md` (Phase 5): note that `init-db` is safe to run twice and does not delete data

## Steps
1. ✅ App factory, config and the `/` page
   - Build: `app/config.py`, `app/__init__.py` (`create_app`), `app/endpoints/page_endpoints.py`,
     placeholder `frontend/login.html`, `tests/api/conftest.py` with `app` and `client` fixtures, first test for `GET /`.
   - Check: run `uv run flask --app app run --debug`, open http://127.0.0.1:5000 → page titled
     "Clinic Booking" with the text "Login comes in feature 3". Terminal shows no errors.
2. ✅ JSON envelope and API 404
   - Build: `app/responses.py`; register a 404 handler in `create_app` that returns
     `failure("Not found", status_code=404)` for paths starting with `/api/` (other paths keep Flask's HTML 404).
   - Check: with the server running, open http://127.0.0.1:5000/api/nope → JSON
     `{"status": false, "message": "Not found", "data": null, "errors": []}`; open
     http://127.0.0.1:5000/nope → normal HTML "Not Found" page.
3. ✅ Database, schema and `init-db`
   - Build: `app/schema.sql`, `app/db.py` (`get_db`, `close_db`, `init_db`, `init-db` command), register in factory;
     `app` fixture now runs `init_db()` on a temp DB.
   - Check: delete `instance/clinic.db` if it exists, run `uv run flask --app app init-db` → prints
     "Initialized the database."; run it a second time → same message, no error; then run
     `uv run python -c "import sqlite3; print(sqlite3.connect('instance/clinic.db').execute(\"select name from sqlite_master where type in ('table','index') and name not like 'sqlite_%' order by name\").fetchall())"`
     → lists `appointments, doctor_hours, doctors, patients, users` and the partial index.
4. ✅ Clock and fixed-clock fixture
   - Build: `app/clock.py` (`now()`), `fixed_now` fixture in `conftest.py`, clock/config tests.
   - Check: run `uv run python -c "from app import clock; print(clock.now())"` → current Karachi time,
     no `+05:00` offset. Then `$env:CLINIC_TZ='UTC'; uv run python -c "from app import clock; print(clock.now())"`
     → 5 hours earlier. Then `Remove-Item Env:CLINIC_TZ`.
5. ✅ Seed placeholder and Postman run
   - Build: `app/seed.py` placeholder `seed` command, register in factory; add the 404 request to the
     Postman collection.
   - Check: `uv run flask --app app seed` → logs "nothing to seed yet", exit without error. Then
     `uv run python scripts/postman_run.py` → Newman shows 2 requests, all assertions pass, last line
     "Postman run: PASSED".

## Test cases
Each case gets an ID so tests and results can refer to it.

### Unit (pure rules in `app/rules/`)
None: this feature adds no pure rules (`app/rules/` starts in feature 5).

### API (`tests/api/`)
- A1: `GET /` → 200, HTML containing "Clinic Booking"
- A2: `success({"x": 1}, "Done")` inside a request context → 200, body
  `{"status": true, "message": "Done", "data": {"x": 1}, "errors": []}`
- A3: `success(..., status_code=201)` → 201
- A4: `failure("Bad input", ["phone is required"], 400)` → 400, `status: false`, `data: null`,
  `errors: ["phone is required"]`; `failure("Bad")` without errors → `errors: []`
- A5: `GET /api/does-not-exist` → 404, `status: false`, `message: "Not found"`, JSON content type
- A6: `GET /does-not-exist` (non-API) → 404, not JSON
- A7: after `init_db()` the DB has tables `users`, `doctors`, `doctor_hours`, `patients`, `appointments`
  and the partial unique index on `appointments`
- A8: `flask init-db` run twice via the CLI runner → exit code 0 both times; a row inserted before the
  second run still exists
- A9: two `booked` appointments with the same `doctor_id` and `start_at` → `sqlite3.IntegrityError`
- A10: one `cancelled` and one `booked` appointment with the same `doctor_id` and `start_at` → both saved
- A11: same `start_at` for two different doctors, both `booked` → both saved
- A12: foreign keys are enforced: appointment with a non-existent `doctor_id` → `sqlite3.IntegrityError`
- A13: CHECK constraints: `doctors.slot_minutes = 25` → IntegrityError; `doctor_hours.weekday = 7` → IntegrityError;
  `appointments.status = 'pending'` → IntegrityError; `users.role = 'nurse'` → IntegrityError
- A14: duplicate `patients.phone` → IntegrityError; duplicate `users.username` → IntegrityError;
  two `doctor_hours` rows for the same doctor and weekday → IntegrityError
- A15: `fixed_now` fixture → `app.clock.now()` returns `datetime(2026, 1, 5, 9, 0)` with `tzinfo is None`
- A16: real `clock.now()` → `tzinfo is None` and within 5 seconds of
  `datetime.now(ZoneInfo("Asia/Karachi")).replace(tzinfo=None)`; with `CLINIC_TZ=UTC` (monkeypatched env)
  → within 5 seconds of UTC now
- A17: config defaults with the env vars unset: `SECRET_KEY == "dev"`, `CLINIC_TZ == "Asia/Karachi"`,
  database path ends with `instance/clinic.db`; with `CLINIC_DATABASE` set → that path is used
- A18: `create_app({"DATABASE": <tmp path>, "TESTING": True})` uses the given path (test config overrides env)
- A19: `flask seed` via the CLI runner → exit code 0

No 401 / 403 / 409 cases: this feature has no login, roles or business endpoints.

### Postman (`postman/clinic.postman_collection.json`)
- P1: 00 Health / Login page is served → 200 (already in the collection)
- P2: 00 Health / Unknown API path returns JSON 404 → 404, `status` is `false`

## Out of scope
- Seed data (doctors, hours, users, patients): feature 2. `seed` is only a placeholder here.
- Login, logout, `auth.py`, `login_required` / `role_required`, role pages, per-role test clients: feature 3.
- The real login page, `css/style.css`, `js/api.js` and other frontend files: features 3 and 9.
- Any business API endpoint and any `app/rules/` file.
- JSON handlers for 405 / 500 (added when the first endpoints need them).
- Migrations: after a schema change, delete the DB file and run `init-db` again.

## Test results (Phase 3, updated in Phase 5)
| Level | Result |
|---|---|
| Unit | no unit cases (no rules in this feature); `tests/unit` collects 0 tests |
| API | 28 passed, 0 failed (re-run in Phase 5 after the review fix: 28 passed) |
| Postman | 2 requests, 3 assertions, 0 failed (PASSED); not re-run in Phase 5: review only changed a test file |

Coverage: each case ID → test name.
- A1 `test_A1_login_page_is_served` · A2 `test_A2_success_envelope` · A3 `test_A3_success_with_status_code_201`
- A4 `test_A4_failure_envelope`, `test_A4_failure_without_errors_gives_empty_list`
- A5 `test_A5_unknown_api_path_returns_json_404` · A6 `test_A6_unknown_page_returns_html_404`
- A7 `test_A7_init_db_creates_tables_and_index` · A8 `test_A8_init_db_twice_keeps_data`
- A9 `test_A9_double_booking_same_doctor_and_start_is_rejected` · A10 `test_A10_cancelled_slot_can_be_booked_again`
- A11 `test_A11_same_start_for_two_doctors_both_saved` · A12 `test_A12_foreign_key_unknown_doctor_is_rejected`
- A13 `test_A13_check_slot_minutes_25_is_rejected`, `test_A13_check_weekday_7_is_rejected`,
  `test_A13_check_weekday_0_and_6_are_accepted`, `test_A13_check_status_pending_is_rejected`, `test_A13_check_role_nurse_is_rejected`
- A14 `test_A14_duplicate_patient_phone_is_rejected`, `test_A14_duplicate_username_is_rejected`,
  `test_A14_duplicate_doctor_hours_same_weekday_is_rejected`
- A15 `test_A15_fixed_now_fixes_the_clock` · A16 `test_A16_real_clock_is_naive_clinic_local`, `test_A16_real_clock_follows_clinic_tz`
- A17 `test_A17_config_defaults`, `test_A17_config_database_from_env` · A18 `test_A18_test_config_overrides_env_database`
- A19 `test_A19_seed_command_runs`
- P1 00 Health / Login page is served · P2 00 Health / Unknown API path returns JSON 404

Spec gaps found: index partial-ness not asserted (A7); completed/no_show blocking a slot untested (A9–A11);
`active` CHECKs and other FKs untested (A12–A13); case-sensitivity of phone/username (A14); invalid `CLINIC_TZ` (A16);
`SECRET_KEY` env override (A17); non-GET on unknown `/api/` path (A5).

## Review summary (Phase 4)
- Code changed in review: yes (files: `tests/api/test_db.py`)
- Must fix: `db` fixture in `tests/api/test_db.py` had no return type → added `-> Iterator[sqlite3.Connection]`
- Should fix applied: none
- Skipped: 1 `fixed_now` docstring note about calling `clock.now()` via the module; 2 time zone read from env and config;
  3 invalid `CLINIC_TZ` fails late; 4 bare `/api` gets HTML 404; 5 `logging.basicConfig` in factory;
  6 no DB check tying `users.doctor_id` to role doctor; 7 test that completed/no_show blocks a slot;
  8 A19 test lives in `test_db.py`

## AI usage
| | Session % | Weekly % |
|---|---|---|
| Before | 12 | 16 |
| After | 10 | 18 |
| Used | n/a (session window reset during the feature) | 2 |
Model(s): main session Opus 5.5; test-writer agent Sonnet; code-reviewer agent Opus
Tokens (from ccusage / tracker): not recorded
