# Seed
Status: done
Plan item: 2
Branch: feature/02-seed

## Goal
A developer can run `uv run flask --app app seed` on a fresh database and get 3 doctors with weekly hours,
the 4 standard logins and 5 patients, ready for the next features. Running it again changes nothing.

## Changes
- `app/repositories/doctor_repository.py`: new. `get_doctor_id_by_name(name)`, `insert_doctor(name, specialty, slot_minutes) -> int`,
  `insert_doctor_hours(doctor_id, weekday, start_time, end_time) -> bool` (`INSERT OR IGNORE`; True if a row was added)
- `app/repositories/user_repository.py`: new. `get_user_by_username(username)`, `insert_user(username, password_hash, role, doctor_id, created_at) -> int`
- `app/repositories/patient_repository.py`: new. `get_patient_by_phone(phone)`, `insert_patient(name, phone, date_of_birth, created_at) -> int`
- `app/seed.py`: replace the placeholder. Sample data as module constants (`DOCTORS`, `USERS`, `PATIENTS`),
  `seed_doctors()`, `seed_users()`, `seed_patients()` each returning `(added, skipped)`, one commit at the end,
  and a summary printed with `click.echo`. Passwords hashed with `werkzeug.security.generate_password_hash`.
  `created_at` = `clock.now()` formatted `YYYY-MM-DDTHH:MM`.
- `tests/api/test_seed.py`: new. Basic tests for the seed command (builder); test-writer adds the rest in Phase 3.
- `tests/api/test_db.py`: unchanged (`test_A19_seed_command_runs` keeps passing).
- `README.md`: one line saying the seed logins are for local development only.

No schema change, no new endpoint, no new dependency.

## Seed data
Doctors (row is found by `name`; if it exists, it and its hours are left alone):

| Name | Specialty | Slot | Weekly hours |
|---|---|---|---|
| Dr Ali Khan | General Physician | 15 min | Mon–Sun (0–6), 09:00–17:00 |
| Dr Sara Ahmed | Pediatrics | 20 min | Mon–Fri (0–4), 10:00–14:00 |
| Dr Bilal Hussain | Dermatology | 30 min | Mon, Wed, Sat (0, 2, 5), 16:00–20:00 |

Users (found by `username`; an existing user is never changed, so a changed password is not reset):

| Username | Password | Role | Linked doctor |
|---|---|---|---|
| `admin` | `admin123` | admin | — |
| `reception` | `reception123` | receptionist | — |
| `drali` | `doctor123` | doctor | Dr Ali Khan |
| `drsara` | `doctor123` | doctor | Dr Sara Ahmed |

Dr Bilal Hussain has no login (bookable, but no doctor page). This keeps the plan's 4 users.

Patients (found by `phone`):

| Name | Phone | Date of birth |
|---|---|---|
| Ahmed Raza | 03001234567 | 1985-03-12 |
| Fatima Noor | 03111234567 | 1992-07-25 |
| Usman Tariq | 03211234567 | — |
| Ayesha Siddiqui | 03331234567 | 2015-11-02 |
| Hamza Iqbal | 03451234567 | 1970-01-30 |

Command output (example, first run then second run):
```
Doctors: 3 added, 0 already there
Doctor hours: 15 added, 0 already there
Users: 4 added, 0 already there
Patients: 5 added, 0 already there
```
```
Doctors: 0 added, 3 already there
Doctor hours: 0 added, 0 already there
Users: 0 added, 4 already there
Patients: 0 added, 5 already there
```
(Hours are only added for doctors created in this run.)

## Steps
Fewer than 5 steps: the feature is one CLI command with three data groups. A 4th step covers the run-twice
summary and the Postman check. A 5th step would be artificial.

1. ✅ Doctors and weekly hours
   - Build: `doctor_repository.py`; in `seed.py` the `DOCTORS` constant, `seed_doctors()`, and the
     "Doctors" + "Doctor hours" summary lines. Basic test: seed on an empty DB → 3 doctors, 15 hours rows.
   - Check: delete `instance/clinic.db`, run `uv run flask --app app init-db`, then `uv run flask --app app seed`
     → output shows `Doctors: 3 added, 0 already there` and `Doctor hours: 15 added, 0 already there`.
2. ✅ Users
   - Build: `user_repository.py`; `USERS` constant and `seed_users()` (hashed passwords, doctor links found by
     doctor name). Basic test: 4 users, `drali` linked to Dr Ali Khan, password hash checks.
   - Check: delete the DB, `init-db`, `seed` → also `Users: 4 added, 0 already there`.
3. ✅ Patients
   - Build: `patient_repository.py`; `PATIENTS` constant and `seed_patients()`. Basic test: 5 patients.
   - Check: delete the DB, `init-db`, `seed` → also `Patients: 5 added, 0 already there`.
4. ✅ Safe to run twice, README, Postman
   - Build: basic test that a second run adds nothing; README note "seed logins are for local development only".
   - Check: run `uv run flask --app app seed` a second time → every line shows `0 added`.
     Then `uv run python scripts/postman_run.py` → Newman passes (the runner seeds `instance/postman.db`).

## Test cases
Each case gets an ID so tests and results can refer to it.

### Unit (pure rules in `app/rules/`)
None. This feature adds no rules (no time or slot logic).

### API (`tests/api/test_seed.py`, through the CLI runner on the temporary DB)
- A1: `seed` on an empty DB → exit code 0; 3 doctors, 15 `doctor_hours` rows, 4 users, 5 patients
- A2: `seed` twice → exit code 0 both times; counts still 3 / 15 / 4 / 5; second output shows `0 added` on every line
- A3: doctors have three different `slot_minutes`, all in (10, 15, 20, 30, 45, 60)
- A4: at least one doctor has hours for all 7 weekdays (0–6)
- A5: the three doctors have different weekly hours (different weekday sets or times)
- A6: every `doctor_hours` row has `start_time < end_time` and at least one full slot fits
  (`end - start >= slot_minutes`), times in `HH:MM`
- A7: users have the right roles; `drali` → Dr Ali Khan, `drsara` → Dr Sara Ahmed; `admin` and `reception` have
  `doctor_id` NULL; all users `active = 1`
- A8: passwords are hashed: no `password_hash` equals its plain password, and `check_password_hash` is true
  for each of the 4 username/password pairs
- A9: patients: 5 rows, phones unique, digits only, 10–15 characters; dates of birth are NULL or `YYYY-MM-DD` before the fixed clock date
- A10: partly seeded DB: insert user `admin` with another password first, then `seed` → `admin` keeps its
  original hash, the other 3 users are added; output `Users: 3 added, 1 already there`
- A11: `created_at` of seeded users and patients equals the fixed clock (`2026-01-05T09:00`, `fixed_now` fixture)

### Postman (`postman/clinic.postman_collection.json`)
- No new requests: seed has no endpoint. P1: `scripts/postman_run.py` (which runs `init-db` + `seed` on a
  fresh `instance/postman.db`) still passes all existing requests.

## Out of scope
- Sample appointments (booking arrives in feature 6).
- Login, roles and sessions (feature 3); seeded users can't log in until then.
- Updating existing rows: seed only adds what is missing, never resets passwords, hours or names.
- A production guard or `--reset` option; delete the DB file to start over (as documented in CLAUDE.md).
- Admin screens to manage doctors/hours/users (out of scope in PLAN.md).

## Test results (Phase 3, updated in Phase 5)
| Level | Result |
|---|---|
| Unit | no tests (no rules in this feature) |
| API | 43 passed (15 in `test_seed.py`) |
| Postman | 2 requests, 3 assertions passed (no new requests) |
Phase 5: re-test skipped: no changes (no code changed in review).
Coverage (all in `tests/api/test_seed.py`):
- A1 `test_A1_seed_on_empty_db_creates_all_rows`
- A2 `test_A2_seed_twice_keeps_counts_and_reports_zero_added`
- A3 `test_A3_doctors_have_three_different_valid_slot_minutes`
- A4 `test_A4_at_least_one_doctor_works_all_seven_weekdays`
- A5 `test_A5_doctors_have_different_weekly_hours`
- A6 `test_A6_every_hours_row_is_valid_and_fits_one_slot`
- A7 `test_A7_users_have_right_roles_links_and_are_active`
- A8 `test_A8_passwords_are_hashed_and_verify`
- A9 `test_A9_patients_have_valid_unique_phones_and_birth_dates`
- A10 `test_A10_partly_seeded_db_keeps_existing_user_and_adds_rest`
- A11 `test_A11_created_at_equals_fixed_clock`
- P1 `scripts/postman_run.py` (seeds a fresh `instance/postman.db`)
Spec gaps found: none needing a change. Existing rows (doctor by name, patient by phone) are never updated
or repaired, as the spec intends (Out of scope: "Updating existing rows").

## Review summary (Phase 4)
- Code changed in review: no
- Must fix: none
- Should fix applied: none
- Skipped (owner's choice): 1 doctor user with missing doctor link gets NULL `doctor_id` (skip + warn);
  2 `-> int` hints vs `lastrowid: int | None`; 3 unused `logger` in `seed.py`; 4 spec says `seed_doctors()`
  returns one pair, it returns two; 5 f-string table name in test helper `count_rows`; 6 builder tests overlap
  A1/A2/A7/A8; 7 seed tests without A11 run on the real clock (no time assertions); 8 re-run Postman
  (already passed in Phase 3)

## AI usage
| | Session % | Weekly % |
|---|---|---|
| Before | 12 | 18 |
| After | 19 | 19 |
| Used | 7 | 1 |
Model(s): Opus 5.5 (main), Sonnet (test-writer), Opus (code-reviewer)
Tokens (from ccusage / tracker): not recorded (agents: test-writer ~24k, code-reviewer ~29k)
