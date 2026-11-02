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

### Backend setup

Backend installation and execution instructions will be added
when the initial Python application is configured.


### Frontend setup

Frontend installation and execution instructions will be added
when the frontend application is configured.


## Configuration

Required environment variables will be documented in `.env.example`
when the application configuration is established.

Do not commit:

- Passwords or API tokens.
- Private keys or other credentials.
- Local `.env` files containing secrets.
- Python virtual environments.
- Installed dependency folders.
- Generated build files.
- Local development databases or real business partner data.
