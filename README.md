# Clinic Booking

Appointment booking for a small clinic: the receptionist books patients into doctors' free slots,
doctors record visit outcomes, admin views reports. Flask + SQLite + plain HTML/CSS/JS.

## Requirements
- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- Git (Git for Windows includes the bash that runs the hooks)
- Node.js (for `npx newman`, the Postman runner)
- Claude Code

## Setup (once)
```powershell
uv init --no-workspace          # only if pyproject.toml does not exist yet
uv add flask tzdata             # tzdata: time zone data, needed on Windows
uv add --dev pytest ruff
git init
git config core.hooksPath .githooks     # removes AI attribution lines from commits
git add .
git commit -m "Project setup: process and Claude Code files"
```
Create an empty GitHub repo, then `git remote add origin <url>` and `git push -u origin main`.

## Run
```powershell
uv run flask --app app init-db
uv run flask --app app seed
uv run flask --app app run --debug
```
Open http://127.0.0.1:5000

`seed` adds sample doctors, patients and the logins `admin/admin123`, `reception/reception123`,
`drali/doctor123`, `drsara/doctor123`. These are for local development only.

## Test
```powershell
uv run pytest -q                       # unit + API tests
uv run python scripts/postman_run.py   # Postman collection against a fresh DB (port 5001)
```

## Build features with Claude Code
```
/model opusplan
/clear
/feature
```
The 7-phase pipeline is described in `docs/PROCESS.md`; the feature list is in `docs/PLAN.md`.
