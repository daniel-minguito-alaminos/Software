# Frontend
Web application of BizPartnerCheck: form to start a Check, display of results, saved Checks and API token management.

## Tech stack

Plain HTML, CSS and JavaScript. No framework, no build step and no dependencies to install.

| File | Purpose |
| --- | --- |
| `index.html` | Access page (public), with links to Log in and Register. |
| `register.html` | Registration form. |
| `login.html` | Login form. |
| `styles.css` | All the styles of the three pages. |
| `app.js` | Backend URL and routes, auth requests, validation and form behaviour. |

## Pages

| Page | Description |
| --- | --- |
| `index.html` | Public landing page with links to Log in and Register. |
| `register.html` | Email, first name, last name and organization number. No password field: the email is verified first. On success it asks the user to check their email. |
| `login.html` | Email and password. There is no "forgot password" link: password resets are done by the Super Admin. |

Both forms check for empty fields and a valid email format before sending anything.

## Install

Nothing to install. You only need a web browser.

## Run

Option A — open the file directly: double-click `frontend/index.html`.

Option B (recommended) — serve the folder with a small local web server, for example with Python
(already used by the backend):

```bash
cd frontend
python -m http.server 5173
```

Then open http://localhost:5173. Other options: the VS Code "Live Server" extension, or
`npx serve` if you have Node.js.

Use option B when testing against the real backend: browsers treat pages opened from `file://`
as having no origin, which causes CORS problems.

## Build

There is no build step: the files in this folder are the final files that are served.

## Backend connection (not verified)

> **The auth endpoints do not exist yet in the backend, and the real connection has not been
> verified.** Until they exist, submitting a form will show an error.

The forms always send their requests to the backend. The URL and the routes are constants at the
top of [`app.js`](app.js), marked as **provisional**:

| Constant | Value | Description |
| --- | --- | --- |
| `API_BASE_URL` | `http://localhost:8000` | Base URL of the backend REST API. |
| `REGISTER_PATH` | `/auth/register` | `POST` with `{ email, firstName, lastName, organizationNumber }`. |
| `LOGIN_PATH` | `/auth/login` | `POST` with `{ email, password }`. |

These values, the request bodies and the status codes are placeholders, not an agreed contract.
The current assumptions are:

- Any `2xx` response means success.
- Register: any other response shows "Registration could not be completed…".
- Login: `401` shows "Incorrect email or password."; any other error response shows
  "Something went wrong…".
- No response at all (server down, wrong URL, CORS blocked) shows the server connection error.
- Session/token handling after login is not implemented yet.

When the backend defines the auth API:

1. Update the constants and, if needed, the `register()` / `login()` functions in section
   "2. AUTH API" of `app.js`.
2. Make sure the backend allows CORS requests from the frontend origin
   (e.g. `http://localhost:5173`).

Do not put secrets in these files: everything in them is visible in the browser.

## States

- **Field validation:** empty fields or an invalid email (e.g. `name@company`) show an error
  under each field, and no request is sent.
- **Waiting:** while the request is in progress, the fields are locked and the button is
  disabled and shows "Loading…".
- **Server connection error:** shown when the backend cannot be reached
  (e.g. when it is not running).
- **Incorrect credentials:** shown on the login page when the backend answers `401`.
- **Registration error:** shown on the register page when the backend rejects the registration.
