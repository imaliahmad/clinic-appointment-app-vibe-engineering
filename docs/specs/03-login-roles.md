# Login & roles
Status: done
Plan item: 3
Branch: feature/03-login-roles

## Goal
A user can sign in on the login page and land on the page for their role (reception, doctor or admin),
see their username, and log out. Opening a page of another role sends them back to their own page;
API endpoints answer 401 when not logged in and 403 for the wrong role.

## Changes
- `app/rules/auth_rules.py`: new. Pure `home_path_for_role(role) -> str` (`receptionist` → `/reception`, `doctor` → `/doctor`, `admin` → `/admin`) and `can_access_page(role, page_role) -> bool`
- `app/repositories/user_repository.py`: add `get_user_by_id(user_id)`
- `app/services/auth_service.py`: new. `authenticate(username, password) -> (user, error)` (checks active flag, `check_password_hash`), `get_current_user(user_id)`
- `app/handlers/auth_handler.py`: new. `login`, `logout`, `me`: validate body, set/clear the session (`user_id`, `role`, `doctor_id`), respond via `responses.py`
- `app/endpoints/auth_endpoints.py`: new. `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- `app/auth.py`: new. `login_required` and `role_required(*roles)` for API routes (JSON 401 / 403) and `page_role_required(role)` for pages (redirects)
- `app/endpoints/page_endpoints.py`: `/` redirects signed-in users to their page; add `/reception`, `/doctor`, `/admin`
- `app/__init__.py`: set the session cookie to `HttpOnly` + `SameSite=Lax`; register `auth_bp`
- `frontend/login.html`: replace placeholder with the login form
- `frontend/reception.html`, `frontend/doctor.html`, `frontend/admin.html`: new page shells (heading, username, Logout button)
- `frontend/js/api.js`: new. The only `fetch()` caller: `login`, `logout`, `getMe`; handles 401 → `/` and 403 → own page
- `frontend/js/login.js`, `frontend/js/reception.js`, `frontend/js/doctor.js`, `frontend/js/admin.js`: new, small
- `frontend/css/style.css`: new, minimal layout only (styling pass is item 9)
- `postman/clinic.postman_collection.json`: fill the `01 Auth` folder
- `tests/unit/test_auth_rules.py`, `tests/api/test_auth.py`: new
- `docs/ARCHITECTURE.md`: only if something differs from what it already says (expected: no change)

No schema change, no new dependency. Passwords are never returned by any endpoint.

## Behaviour
- Login success: 200, `data = {id, username, role}`, session cookie set.
- Missing/blank `username` or `password` or a non-JSON body: 400. Unknown user, wrong password or inactive user: 401 with the same message ("Invalid username or password") so it does not reveal which one was wrong.
- `GET /api/auth/me`: `{id, username, role, doctor_id}`. Not logged in: 401.
- Logout clears the session; logging out when not logged in is 401 (it requires login, as in the API table).
- Pages: not logged in → redirect to `/`. Logged in with another role → redirect to that user's own page.
- A session whose user no longer exists or is inactive counts as not logged in (session is cleared, 401).

## Steps
1. ✅ Role rules and auth API
   - Build: `auth_rules.py`, `get_user_by_id`, `auth_service.py`, `auth_handler.py`, `auth_endpoints.py`, `login_required` in `app/auth.py`, register the blueprint, session cookie settings.
   - Check: start the app (`uv run flask --app app run --debug`, after `init-db` and `seed`). In a second terminal: `curl -i -c jar -H "Content-Type: application/json" -d '{"username":"drali","password":"doctor123"}' http://127.0.0.1:5000/api/auth/login` → 200 with `role: doctor`; `curl -b jar http://127.0.0.1:5000/api/auth/me` → 200 with `doctor_id`; wrong password → 401; `curl http://127.0.0.1:5000/api/auth/me` (no cookie) → 401.
2. ✅ `role_required` and the role pages
   - Build: `role_required` and `page_role_required` in `app/auth.py`; `/reception`, `/doctor`, `/admin` and the `/` redirect in `page_endpoints.py`; three plain page shells.
   - Check: `curl -i http://127.0.0.1:5000/reception` → 302 to `/`. With the doctor cookie jar: `/doctor` → 200, `/admin` → 302 to `/doctor`, `/` → 302 to `/doctor`.
3. ✅ Login page
   - Build: `login.html`, `js/api.js` (`login`, `getMe`), `js/login.js`, minimal `style.css`. Form shows the server `message` on failure and redirects by role on success.
   - Check: open http://127.0.0.1:5000/ . Log in as `reception` / `reception123` → lands on `/reception`. Wrong password → red message, stays on the page. Repeat for `drali` → `/doctor`, `admin` → `/admin`. Console (F12): no errors.
4. ✅ Page shells: username, Logout, redirects
   - Build: `api.js` gets `logout` and the 401/403 handling; `reception.js`, `doctor.js`, `admin.js` show the username (via `getMe`) and wire the Logout button (`textContent` only).
   - Check: each page shows the signed-in username and a Logout button. Logout → back at `/`, and pressing Back then reloading `/reception` redirects to `/`. Logged in as `drali`, typing `/admin` in the address bar lands on `/doctor`.
5. ✅ Postman and docs
   - Build: `01 Auth` Postman folder (login ok, login wrong password, me, me without login, logout); check `docs/ARCHITECTURE.md` against the final behaviour.
   - Check: `uv run python scripts/postman_run.py` → all requests pass.

## Test cases
Each case gets an ID so tests and results can refer to it.

### Unit (pure rules in `app/rules/`)
- U1: `home_path_for_role("receptionist")` → `/reception`
- U2: `home_path_for_role("doctor")` → `/doctor`
- U3: `home_path_for_role("admin")` → `/admin`
- U4: `home_path_for_role("nurse")` (unknown role) → raises `ValueError`
- U5: `can_access_page("doctor", "doctor")` → True
- U6: `can_access_page("doctor", "admin")` → False
- U7: `can_access_page("admin", "receptionist")` → False (admin has no access to other roles' pages)

### API (`tests/api/`)
- A1: login as `reception` with correct password → 200, `data` has `id`, `username`, `role: receptionist`, no password field; session cookie set
- A2: login as `drali` → 200, then `GET /api/auth/me` → `doctor_id` equals Dr Ali Khan's id
- A3: login with a wrong password → 401, `status: false`
- A4: login with an unknown username → 401, same message as A3
- A5: login for a user with `active = 0` → 401
- A6: login with missing `password`, blank `username`, or no JSON body → 400, `status: false`
- A7: `GET /api/auth/me` not logged in → 401
- A8: `POST /api/auth/logout` logged in → 200, then `GET /api/auth/me` → 401
- A9: `POST /api/auth/logout` not logged in → 401
- A10: session of a user deactivated after login → `GET /api/auth/me` → 401
- A11: `role_required("admin")` on a test route, logged in as receptionist → 403, `status: false`
- A12: `role_required("admin")` on a test route, not logged in → 401
- A13: `GET /reception` not logged in → 302 to `/`
- A14: `GET /doctor` as receptionist → 302 to `/reception`
- A15: `GET /admin` as admin → 200 HTML
- A16: `GET /` logged in as doctor → 302 to `/doctor`; not logged in → 200 login page
- A17: session cookie has `HttpOnly` and `SameSite=Lax`

### Postman (`postman/clinic.postman_collection.json`)
- P1: 01 Auth / Login as reception → 200, `status: true`, role `receptionist`
- P2: 01 Auth / Login with wrong password → 401, `status: false`
- P3: 01 Auth / Me (logged in) → 200, username `reception`
- P4: 01 Auth / Logout → 200
- P5: 01 Auth / Me after logout → 401

## Out of scope
- Registering users, changing or resetting passwords, "remember me", login rate limiting (not in `docs/PLAN.md`)
- CSRF tokens (local learning project; `SameSite=Lax` only)
- Any patient, slot or booking UI or endpoint (items 4–7); the page shells have no content beyond username and Logout
- Final styling (item 9)

## Test results (Phase 3, updated in Phase 5)
| Level | Result |
|---|---|
| Unit | 16 passed |
| API | 76 passed |
| Postman | 7 requests, 15 assertions, all passed |
Coverage (all in `tests/unit/test_auth_rules.py` and `tests/api/test_auth.py`; A-tests are in the API file):
- U1-U3 `test_U1_U3_home_path_for_role` · U4 `test_U4_unknown_role_raises` · U5 `test_U5_own_page_allowed` · U6 `test_U6_other_page_denied` · U7 `test_U7_admin_has_no_access_to_other_roles_pages`
- A1 `test_A1_login_success` · A2 `test_A2_doctor_login_me_has_doctor_id` · A3 `test_A3_wrong_password_returns_401` · A4 `test_A4_unknown_username_returns_401_same_message` · A5 `test_A5_inactive_user_login_returns_401` · A6 `test_A6_*` (7 tests) · A7 `test_A7_me_without_login_returns_401` · A8 `test_A8_logout_clears_session` · A9 `test_A9_logout_without_login_returns_401` · A10 `test_A10_deactivated_user_session_returns_401` · A11 `test_A11_wrong_role_returns_403` · A12 `test_A12_admin_route_without_login_returns_401` · A13 `test_A13_page_without_login_redirects_to_login` · A14 `test_A14_other_role_page_redirects_to_own_page` · A15 `test_A15_admin_page_as_admin_returns_html` · A16 `test_A16_login_page_redirects_signed_in_user` · A17 `test_A17_session_cookie_is_httponly_and_samesite_lax`
- P1-P5: Postman folder `01 Auth` (Login as reception, Login with wrong password, Me (logged in), Logout, Me after logout)
Extra test (not a spec ID): login assets are served but HTML pages are not under `/static`.
Fixed during testing: nothing.
Re-test after review: skipped, no changes (final numbers: 16 unit, 76 API, Postman 7 requests / 15 assertions).
Spec gaps found: 8 minor ones (username case/trim, re-login while logged in, null doctor_id, non-object JSON, messages, stale page session, 405 on pages, no real 403 endpoint yet). Accepted as is at Gate 3; no spec change.

## Review summary (Phase 4)
- Code changed in review: no (files: none; only the spec file's encoding was repaired, docs only)
- Must fix: none from the reviewer. Self-found: invalid bytes in this spec file, repaired.
- Should fix applied: none (chose `none`)
- Skipped: 1 PAGES map duplicated in the browser; 2 spec Changes list missing static route / static_folder / ARCHITECTURE line; 4 login timing difference; 5 `assert` in `me` handler; 6 `auth.py` docstring; 7 near-duplicate tests; 8 unknown role would 500

## AI usage
| | Session % | Weekly % |
|---|---|---|
| Before | 21% | 19% |
| After | 27% | 20% |
| Used | 6 | 1 |
Model(s): Opus 5.5 (spec planning), Sonnet 5.5 (build), Sonnet (test-writer), Opus (code-reviewer)
Tokens (from ccusage / tracker): not recorded (agents ~30k + ~42k)
