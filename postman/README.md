# Postman collection

`clinic.postman_collection.json` has a request for every endpoint, grouped in folders that run in order.
Every new endpoint adds its requests here (see the `add-endpoint` skill); spec case IDs `P1, P2, …` refer to them.

## Run (recommended)
```powershell
uv run python scripts/postman_run.py
```
It deletes and recreates `instance/postman.db` (init-db + seed), starts the server on port 5001,
runs Newman, stops the server, and exits with 0 (passed) or 1 (failed). Your dev server on 5000 is not touched.

## Run in the Postman app
Import both files, select the `local` environment (baseUrl `http://127.0.0.1:5000`),
start your dev server, and use Collection Runner. This uses your dev database.

## Writing requests
- Folder order: 00 Health → 01 Auth → 02 Patients → 03 Slots → 04 Appointments → 05 Schedules → 06 Admin → 07 Access checks.
- The session cookie from a login request is reused by the requests after it in the same run.
  Log in as the role a folder needs at the start of that folder.
- Every request has a test script checking the status code and the `status` field.
- Booking needs a future date: set `bookingDate` in a pre-request script (e.g. tomorrow),
  and use the seeded doctor who works every day.
- Save ids you need later in collection variables (`patientId`, `appointmentId`).
