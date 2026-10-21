# LifeLink

LifeLink is an academic blood donor and request project. This repository contains the Django API backend and its registration endpoints.

## Current API

- `GET /api/lookups/` returns blood types and Quezon City barangays for registration forms.
- `POST /api/register/` registers an account as a requester or donor.

See [REGISTRATION_API.md](REGISTRATION_API.md) for request fields, JSON examples, and error responses.

## Run locally

You need Python and access to a PostgreSQL database. Supabase can provide the PostgreSQL database.

1. Clone the repository and open its folder:

   ```bash
   git clone https://github.com/ian07212006-dotcom/LifeLink.git
   cd LifeLink
   ```

2. Create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv .venv
   # Windows Command Prompt
   .venv\Scripts\activate
   # Then install dependencies
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and set your database connection:

   ```dotenv
   DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
   ```

   Keep `.env` local; it is excluded from Git. `CARTO_API_KEY` can also be set there for map-related functionality.

4. Apply migrations and start Django:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Open `http://127.0.0.1:8000/api/lookups/` to view the registration lookup data. Use an API client such as Postman to send JSON to `http://127.0.0.1:8000/api/register/`.

## Scope

The current documented API scope is registration and registration lookup data. Blood-request creation, donor matching, login, and notifications are not included in the registration API contract yet.
