# Clinic Booking: Architecture

## Overview
```
Browser (HTML/CSS/JS) ──fetch JSON──▶ Flask ──▶ endpoints → handlers → services → repositories ──▶ SQLite
                                       │                                   └─► rules (pure functions)
                                       └── serves frontend/ pages
```
Login state: Flask session cookie (`user_id`, `role`, `doctor_id` for doctors).

## Code layout
```
app/
  __init__.py  config.py  clock.py  db.py  schema.sql  seed.py  auth.py  responses.py
  endpoints/     auth_endpoints.py, page_endpoints.py, doctor_endpoints.py, patient_endpoints.py,
                 appointment_endpoints.py, schedule_endpoints.py, report_endpoints.py
  handlers/      one per endpoint file (e.g. appointment_handler.py)
  services/      auth_service.py, doctor_service.py, patient_service.py, appointment_service.py,
                 schedule_service.py, report_service.py
  rules/         slot_rules.py, appointment_rules.py   (pure, no DB/Flask/clock)
  repositories/  user_repository.py, doctor_repository.py, patient_repository.py, appointment_repository.py
frontend/        login.html, reception.html, doctor.html, admin.html, css/style.css,
                 js/api.js, js/format.js, js/login.js, js/reception.js, js/doctor.js, js/admin.js
tests/
  unit/          test_slot_rules.py, test_appointment_rules.py
  api/           conftest.py (app with temp DB, fixed clock, logged-in clients per role),
                 test_auth.py, test_patients.py, test_slots.py, test_appointments.py, test_schedules.py, test_reports.py
postman/         clinic.postman_collection.json, local.postman_environment.json
scripts/         postman_run.py
```
This is the target; files appear as features add them.

## Roles
| Role | Can |
|---|---|
| `receptionist` | search/register patients, view slots, book, cancel, view day schedule of all doctors |
| `doctor` | view own schedule, mark own appointments completed / no-show |
| `admin` | view reports |

## Data model
| Table | Columns |
|---|---|
| `users` | id, username (unique), password_hash, role (`admin` \| `receptionist` \| `doctor`), doctor_id → doctors (only for role doctor), active (0/1), created_at |
| `doctors` | id, name, specialty, slot_minutes (10, 15, 20, 30, 45 or 60), active (0/1) |
| `doctor_hours` | id, doctor_id → doctors, weekday (0=Mon … 6=Sun), start_time `HH:MM`, end_time `HH:MM`; unique (doctor_id, weekday) |
| `patients` | id, name, phone (unique, digits only), date_of_birth (optional `YYYY-MM-DD`), created_at |
| `appointments` | id, doctor_id → doctors, patient_id → patients, start_at, end_at (`YYYY-MM-DDTHH:MM`), status, cancel_reason, created_by → users, created_at, updated_at |

Database guard against double booking: a **partial unique index** on
`appointments(doctor_id, start_at) WHERE status != 'cancelled'`.

`init-db` runs `schema.sql` with `CREATE ... IF NOT EXISTS`: safe to run twice, never deletes data.
There are no migrations: after a schema change, delete the database file and run `init-db` (and `seed`) again.

## Configuration (environment variables)
| Variable | Default | Used for |
|---|---|---|
| `SECRET_KEY` | `dev` | Flask session signing |
| `CLINIC_TZ` | `Asia/Karachi` | clinic time zone |
| `CLINIC_DATABASE` | `instance/clinic.db` | SQLite file (Postman runs use `instance/postman.db`) |

## Time rules
- One clinic time zone: `CLINIC_TZ`. All stored times are clinic-local, no offset.
- "Now" comes only from `app/clock.py`. Services pass it into `app/rules/`. Tests fix it.
- On Windows, `zoneinfo` needs the `tzdata` package (`uv add tzdata`).

## Slot rules (`GET /api/doctors/<id>/slots?date=YYYY-MM-DD`)
1. The date must be from today to today + 30 days (clinic-local). Otherwise 400.
2. If the doctor has no hours on that weekday (or is inactive) → empty list.
3. Slots start at `start_time` and step by `slot_minutes`; a slot is included only if it ends at or before `end_time`.
4. Slots already taken by a non-cancelled appointment are excluded.
5. For today, slots whose start time is not after `now` are excluded.

Example: a doctor works 09:00–10:00 with 20-minute slots → `09:00, 09:20, 09:40`.
With 45-minute slots → `09:00` only (09:45 would end at 10:30, after closing).

## Patient rules
- `phone`: digits only, 10–15 characters, unique (duplicate → 409).
- `name`: required, max 100 characters. `date_of_birth`: optional, `YYYY-MM-DD`, not in the future.

## Booking rules (`POST /api/appointments`)
- The requested `start_at` must be one of the slots the slot rules return for that doctor and date.
- The patient must not have another non-cancelled appointment overlapping the same time (any doctor).
- `end_at` is calculated on the server: `start_at + slot_minutes`.

## Status changes
| From | To | Who | When |
|---|---|---|---|
| `booked` | `cancelled` | receptionist | before `start_at`; reason required |
| `booked` | `completed` | the appointment's doctor | at or after `start_at` |
| `booked` | `no_show` | the appointment's doctor | at or after `start_at` |
Any other change → 409, `status: false`.

## API
| Method | Path | Role | Body / query → data |
|---|---|---|---|
| POST | `/api/auth/login` | none | `{username, password}` → `{id, username, role}` |
| POST | `/api/auth/logout` | any | — |
| GET | `/api/auth/me` | any | → `{id, username, role, doctor_id}` |
| GET | `/api/doctors` | receptionist | → `[{id, name, specialty, slot_minutes}]` |
| GET | `/api/doctors/<id>/slots` | receptionist | `?date=` → `["09:00", "09:15", …]` |
| GET | `/api/patients` | receptionist | `?phone=` → `[{id, name, phone, date_of_birth}]` |
| POST | `/api/patients` | receptionist | `{name, phone, date_of_birth?}` → patient |
| GET | `/api/patients/<id>/appointments` | receptionist | → patient's appointments, newest first |
| POST | `/api/appointments` | receptionist | `{doctor_id, patient_id, start_at}` → appointment |
| POST | `/api/appointments/<id>/cancel` | receptionist | `{reason}` → appointment |
| POST | `/api/appointments/<id>/complete` | doctor (own) | → appointment |
| POST | `/api/appointments/<id>/no-show` | doctor (own) | → appointment |
| GET | `/api/appointments` | receptionist | `?date=` → all doctors' appointments that day |
| GET | `/api/doctor/schedule` | doctor | `?date=` → own appointments that day |
| GET | `/api/admin/reports/daily` | admin | `?date=` → appointments per doctor that day |
| GET | `/api/admin/reports/by-doctor` | admin | `?from=&to=` → per doctor: booked, completed, no_show, cancelled |

All responses: `{"status", "message", "data", "errors"}`.

## Pages
| URL | File | Access |
|---|---|---|
| `/` | `login.html` | public; signed-in users go to their role's page |
| `/reception` | `reception.html` | receptionist |
| `/doctor` | `doctor.html` | doctor |
| `/admin` | `admin.html` | admin |
A signed-in user opening another role's page is redirected to their own page.
