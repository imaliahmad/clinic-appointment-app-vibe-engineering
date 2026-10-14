# Frontend rules (frontend/)

Plain HTML, CSS and JavaScript. No frameworks, no CDN libraries, no build step.

## Files
- `login.html` + `js/login.js`           login form; redirects by role after login
- `reception.html` + `js/reception.js`   patient search/register, booking, day view, cancel
- `doctor.html` + `js/doctor.js`         doctor's own schedule, mark completed / no-show
- `admin.html` + `js/admin.js`           reports
- `js/api.js`                            the ONLY file that calls `fetch()`; one function per endpoint
- `js/format.js`                         date/time display helpers
- `css/style.css`                        all styles

## Rules
- Every backend call goes through `js/api.js`. Pages never call `fetch()` directly.
- Show data with `textContent` or `createElement`, never `innerHTML` with server data.
- Never calculate slots, availability or allowed status changes in the browser. Always ask the API.
- Display times as returned by the API (clinic-local); format them only through `js/format.js`.
- Use `<dialog>` for confirmations (e.g. cancel with reason).
- If an API call returns `status: false`, show `message` to the user. 401 → go to login. 403 → go to the user's own page.
- After any change (book, cancel, complete), reload the affected list from the API; don't patch it locally.
- Clear, large buttons; the receptionist works fast with patients waiting.
- Each page shows the logged-in username and a Logout button.

## Manual checks (Gate 2)
- Test in the browser with the dev server and seeded users.
- Open the browser console (F12): no errors.
