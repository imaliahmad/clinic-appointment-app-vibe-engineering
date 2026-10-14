# Clinic Booking: Plan

## Goal
A receptionist can book a patient into a free slot with a doctor within the next 30 days.
Doctors see their schedule and record the outcome of each visit. Admin sees two reports.

## Features (build in this order, one branch each)
- [x] 1. Skeleton: app factory, `config.py`, `clock.py`, `responses.py`, `db.py`, `schema.sql` (all tables + partial unique index), `init-db`, `tests/api/conftest.py` (temporary DB + fixed-clock fixture), `scripts/postman_run.py` passing on the Health request
- [ ] 2. Seed: 3 doctors (different slot lengths and weekly hours; at least one doctor works all 7 days so Postman runs work on any date), users `admin/admin123`, `reception/reception123`, `drali/doctor123`, `drsara/doctor123` (linked to doctors), 5 patients. Safe to run twice. Local dev only.
- [ ] 3. Login & roles: login/logout/me, `role_required`, page shells for reception/doctor/admin, redirect by role after login, wrong-role pages redirect to the user's own page
- [ ] 4. Patients: search by phone, register a new patient (phone unique, digits only), patient's appointment history (API + reception UI)
- [ ] 5. Available slots: `app/rules/slot_rules.py` (pure, unit-tested) + `GET /api/doctors` and `GET /api/doctors/<id>/slots?date=` (API only)
- [ ] 6. Book & cancel: `app/rules/appointment_rules.py` (overlap + status rules), create appointment (no double booking, no patient overlap), cancel with reason (API + reception booking UI)
- [ ] 7. Schedules: reception day view (all doctors) and doctor's own schedule with complete / no-show
- [ ] 8. Admin reports: daily overview and appointments per doctor by status for a date range
- [ ] 9. Styling pass: clean, readable, consistent across all pages

## Out of scope
Patient self-booking or patient accounts, SMS/email reminders, payments, medical notes or prescriptions,
visit types with different durations, doctor days off and breaks, rescheduling (cancel and book again),
recurring appointments, admin screens to manage doctors/hours/users, multiple clinics, Docker, deployment, CI.
