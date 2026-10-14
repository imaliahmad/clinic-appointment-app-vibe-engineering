# Backend rules (app/)

## Layers (one direction only)
endpoints → handlers → services → repositories → SQLite
                         └─► rules (pure functions)

| Layer | Folder | Does | Never does |
|---|---|---|---|
| Endpoint | `endpoints/` | Flask blueprint route, `login_required` / `role_required`, call handler | Logic, SQL |
| Handler | `handlers/` | Read and validate request input (formats, required fields), call service, build JSON via `responses.py` | SQL, business rules |
| Service | `services/` | Load data via repositories, get `now` from `clock.now()`, call rules, save results, return `(data, error)` | SQL, Flask `request`, time maths itself |
| Rules | `rules/` | **Pure functions**: inputs in, result out. Slot generation, overlap checks, booking window, allowed status changes | Database, Flask, `clock`, I/O of any kind |
| Repository | `repositories/` | SQL queries, return plain dicts/lists | Business rules, formatting |

## Pure rules (`app/rules/`)
- `slot_rules.py`: e.g. `generate_slots(day, hours, slot_minutes, booked_starts, now) -> list[str]`,
  `is_within_booking_window(day, today) -> bool`
- `appointment_rules.py`: e.g. `overlaps(a_start, a_end, b_start, b_end) -> bool`,
  `can_change_status(current, target, role, is_own, start_at, now) -> tuple[bool, str]`
- Every function receives `now` / `today` as an argument. Never import `clock` here.
- Every function has unit tests in `tests/unit/test_{topic}_rules.py`, including boundary cases.

## Shared files
- `__init__.py`   app factory `create_app()`, registers blueprints and CLI commands
- `config.py`     reads `SECRET_KEY`, `CLINIC_TZ`, `CLINIC_DATABASE` from the environment with dev fallbacks
- `clock.py`      `now()` returns the current clinic-local datetime. The ONLY place that reads the real clock.
- `db.py`         `get_db()` connection per request, `init-db` command
- `schema.sql`    all CREATE TABLE / INDEX statements
- `seed.py`       `seed` command: sample doctors, weekly hours, users, patients
- `auth.py`       `login_required` and `role_required(*roles)` decorators
- `responses.py`  `success(data, message)` / `failure(message, errors, status_code)` helpers

## Rules
- All SQL lives in `repositories/`. Always parameterized (`?`). Never f-strings in SQL.
- All time maths lives in `rules/`; services pass in `clock.now()`.
- Status changes follow the table in `docs/ARCHITECTURE.md`. Any other change is rejected with 409.
- Every handler response is built with `responses.py`. Never return a raw dict.
- Every API endpoint except login requires `login_required`; role-specific endpoints use `role_required`.
- Admin-only endpoints live under `/api/admin/`.
- Passwords are hashed with `werkzeug.security`. Never store plain text.
- New endpoint: use the `add-endpoint` skill.

## HTTP status codes
| Case | Code |
|---|---|
| OK / created | 200 / 201 |
| Invalid input (format, missing field, date outside window) | 400 |
| Not logged in | 401 |
| Wrong role / not your appointment | 403 |
| Unknown id | 404 |
| Conflict (slot taken, patient overlap, status change not allowed, duplicate phone) | 409 |
