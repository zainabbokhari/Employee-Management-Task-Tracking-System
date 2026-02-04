Quick runbook — how to run and create admin users

1) Create & activate virtualenv (PowerShell)

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2) Install deps

   python -m pip install --upgrade pip
   pip install -r requirements.txt

3) Create .env (don't commit this file) — edit values for production

   Copy-Item .env.example .env
   notepad .env

4) Create admin (recommended in production)

   python scripts/create_admin.py

5) Run migrations

   python -m alembic upgrade head

6) Start app

   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

7) API docs: http://127.0.0.1:8000/docs

Security notes:
- Keep `.env` out of source control and use secrets manager in production.
- Set `DEBUG=False`, `CREATE_DEMO_USERS=False`, and `ALLOW_PUBLIC_REGISTRATION=False` in production.

Running with Docker (quick)
 
1) Prepare environment

   Copy-Item .env.example .env
   Edit `.env` and set production values (SECRET_KEY, DATABASE_URL, FRONTEND_URL, SMTP_* if using email).

2) Build the image (optional) and start services using Docker Compose (PowerShell):

   docker-compose build; docker-compose up -d

   Or to rebuild and stream logs in one line:

   docker-compose up --build

3) View logs and status (PowerShell):

   docker-compose logs -f web
   docker-compose ps

Notes:
- The provided `docker-compose.yml` brings up a MySQL service and the web service. The `scripts/entrypoint.sh`
  runs Alembic migrations on container start before launching Uvicorn, so migrations are applied automatically.
- Replace the sample DB credentials in `docker-compose.yml` with secure values or provide them via a secrets manager.
- For local development you can continue using the SQLite fallback by setting `DATABASE_URL=sqlite:///./dev.db` in `.env`.
- On Windows, ensure Docker Desktop is running and you have sufficient resources assigned for the database container.
