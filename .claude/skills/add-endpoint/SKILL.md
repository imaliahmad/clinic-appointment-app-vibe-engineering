---
name: add-endpoint
description: Use when adding or changing an API endpoint in the Clinic Booking backend (app/).
---

# Add an API endpoint

1. Read `docs/ARCHITECTURE.md` (API table, data model, time/slot/booking rules, status changes)
   and `app/CLAUDE.md` (layers, pure rules, status codes).
2. If a similar endpoint exists, read all of its layer files first and copy the pattern.
3. Build from the bottom up:
   1. **Rules** (`app/rules/{topic}_rules.py`), only if the endpoint has date/time/overlap/status logic:
      pure functions that take `now` / `today` as arguments. Add unit tests in `tests/unit/`.
   2. **Repository** (`app/repositories/{entity}_repository.py`): SQL with `?` placeholders, returns dicts.
   3. **Service** (`app/services/{entity}_service.py`): load data, get `clock.now()`, call rules,
      save results, return `(data, error)`.
   4. **Handler** (`app/handlers/{entity}_handler.py`): validate input (dates `YYYY-MM-DD`,
      times `YYYY-MM-DDTHH:MM`, required fields), call service, respond via `responses.py`
      with the status codes from `app/CLAUDE.md`.
   5. **Endpoint** (`app/endpoints/{entity}_endpoints.py`): route + `login_required` / `role_required`,
      call handler; register the blueprint in `app/__init__.py` if it is new.
4. Basic API tests in `tests/api/test_{area}.py` using the `conftest.py` fixtures (fixed clock):
   happy path, one invalid input (400), not logged in (401), wrong role (403).
   The test-writer agent adds the full set in Phase 3.
5. Run `uv run pytest -q` until it passes.
6. Add a request to `postman/clinic.postman_collection.json` in the right folder, with a test script that checks
   the status code and the `status` field: one happy path + one error case.
   Requests that need login go after the login request in the same run.
7. Add or update the row in the API table in `docs/ARCHITECTURE.md`.
