# BizPartnerCheck

BizPartnerCheck is a web application and REST API designed to help
construction companies in Austria check their business partners
before entering into a business relationship.

## Why this project exists

Business partner checks involve information from several external
sources. Performing these checks manually takes time and makes it
difficult to keep the results together.

BizPartnerCheck aims to bring these checks into one application
and store the results with supporting evidence for later review.

## Project status

The project is currently under development.


## Planned features

- Organization registration with email verification.
- User access management with four user roles.
- Separation of data between organizations.
- Business partner checks initiated through the web application
  or REST API.
- VAT number validation through VIES.
- Checks against the Austrian Ministry of Finance's fake-company list.
- HFU-List status checks.
- Company registration checks through the Austrian Company Register.
- Business registration and license checks through GISA.
- Person-based cross-checking.
- Individual check results and an overall summary.
- Saved check results and supporting evidence for later review.
- API token administration through the web application.
- Deletion of organization data through the housekeeping process.
- English and German language support.


## External sources

| Source | Purpose |
| --- | --- |
| VIES — European Commission | VAT number validation |
| Fake Company List — Austrian Ministry of Finance | Identification of listed fake companies |
| HFU-List — ÖGK | HFU-List status |
| Austrian Company Register — Ministry of Justice | Company registration information |
| GISA | Business registration and license information |


## Repository structure

- `backend/` — backend application, REST API, and external integrations.
- `frontend/` — web application.
- `README.md` — project overview and development instructions.

### Backend setup — Windows PowerShell

Prerequisite: Python 3 with the `py` launcher installed.

From the repository root:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copy `backend/.env.example` to `backend/.env` and fill in the values:

```dotenv
DATABASE_URL="postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
JWT_SECRET_KEY="<random secret, at least 32 characters>"
JWT_EXPIRE_MINUTES=60
SESSION_COOKIE_SECURE=false
```

- `DATABASE_URL`: the PostgreSQL connection URL supplied by the team.
  Use the External Database URL when connecting from your laptop.
- `JWT_SECRET_KEY`: signs the session tokens. Generate one with
  `.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"`.
- `JWT_EXPIRE_MINUTES`: how long a login session lasts.
- `SESSION_COOKIE_SECURE`: must be `true` in production (HTTPS);
  `false` for local development over HTTP.

Keep `.env` excluded from Git.

Start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

- API health: http://127.0.0.1:8000/health
- Database connection check: http://127.0.0.1:8000/health/database
- API documentation: http://127.0.0.1:8000/docs

Stop the server with Ctrl+C.

#### Test user (provisional)

Registration and email verification are not implemented yet
(BIZ-24 / BIZ-12). To log in, create a verified test user. The password
is asked for interactively:

```powershell
.\.venv\Scripts\python.exe -m scripts.create_test_user tester@example.com
```

The script creates the `users` table if needed. If the email already
exists, its password is replaced and the user is marked as verified.

The `User` model in `backend/models.py` is provisional (BIZ-32); the
final user and organization schema (BIZ-34) will replace or extend it.

#### Backend tests

The tests use an in-memory SQLite database and never connect to the
shared database.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
```

#### Authentication endpoints

The session is a JWT stored in the HttpOnly cookie `bpc_session`.
All session handling lives in `backend/auth_session.py`; protect an
endpoint with the `CurrentUser` dependency from that module.

| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/login` | Body `{"email", "password"}`. Sets the session cookie. `401` for wrong credentials, `403` for unverified accounts. |
| POST | `/auth/logout` | Clears the session cookie. Returns `204`. |
| GET | `/auth/me` | Protected. Returns the logged-in user, or `401`. |

### Frontend setup — Windows PowerShell

Prerequisite: A Node.js version supported by `frontend/package.json`.

Open a separate terminal. From the repository root:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open the Local URL printed in the terminal, usually
http://localhost:5173/.

Create a production build:

```powershell
npm.cmd run build
```

The build output is generated in `frontend/dist/`.

Stop the development server with Ctrl+C.

#### API proxy

During development the frontend calls the backend through the Vite
proxy configured in `frontend/vite.config.js`. Requests to `/api/*`
are forwarded to `http://127.0.0.1:8000` with the `/api` prefix
removed:

| Frontend request | Backend endpoint |
| --- | --- |
| `/api/auth/login` | `/auth/login` |
| `/api/auth/logout` | `/auth/logout` |
| `/api/auth/me` | `/auth/me` |

Backend routes are therefore defined without `/api`. Because the
browser sees a single origin, the session cookie works without CORS.
Start the backend before logging in from the frontend.

#### Login and logout

- `/login` signs in verified users and opens `/app`.
- `/app` is a protected page; visitors without a session are redirected
  to `/login`.
- **Log out** in the header ends the session and returns to the home page.

The registration page is still a UI preview; registration and email
verification are pending (BIZ-24 / BIZ-12).

## Configuration

Backend environment variables are listed in `backend/.env.example`
(see Backend setup above).

Do not commit:

- Passwords or API tokens.
- Private keys or other credentials.
- Local `.env` files containing secrets.
- Python virtual environments.
- Installed dependency folders.
- Generated build files.
- Local development databases or real business partner data.
