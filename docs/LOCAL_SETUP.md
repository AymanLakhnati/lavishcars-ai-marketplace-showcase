# Local setup

The prototype is a Next.js storefront and FastAPI/SQLAlchemy service. PostgreSQL is the target database. SQLite is available for lightweight local execution and isolated tests. These commands use synthetic demo data only.

## Docker Compose

Requires Docker Compose. From the repository root:

```sh
cp .env.example .env
docker compose up --build
```

Open http://localhost:3000. API documentation: http://localhost:8000/docs. Compose runs migrations and the demo seed. It is configured for local use with loopback ports and development credentials; do not expose those defaults on the Internet. Docker itself was unavailable on the development machine, so the directly launched services were used for verification.

## Python and Node on Windows

Requires Python 3.12+ and Node 22+. Run these from the repository root in PowerShell:

```powershell
cd services/api
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m app.seed
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Without `DATABASE_URL`, this uses a persistent local SQLite database. For PostgreSQL, start `npm ci` and `npm run db:local` in another terminal at the root, then set the SQLAlchemy PostgreSQL URL before the migration/seed/API commands. The local helper uses database `lavish` on port 54329, user `lavish` and the documented development-only password `lavish_local_only`.

In a second terminal from the repository root:

```powershell
cd apps/web
npm ci
npm run dev
```

Keep both terminals open. Open http://localhost:3000. Development defaults to direct API requests at http://localhost:8000/api/v1. Production builds instead can use `NEXT_PUBLIC_API_URL=/api/v1` with server-side `API_INTERNAL_ORIGIN=http://127.0.0.1:8000`; see `DEPLOYMENT.md` for that configuration. `START-DEMO.cmd` starts an already-built production storefront when the local API/database are already running.

On macOS/Linux, use `.venv/bin/python` in place of `.venv/Scripts/python`; the remaining commands are equivalent.

## Demo identities

The seed creates `admin@lavish.demo`, `supplier@lavish.demo`, `pending@lavish.demo` and `houston@lavish.demo`. Set `DEMO_PASSWORD` before first seeding to choose the local password; its local default is `DemoDrive!2026`. Use distinct browser profiles for supplier/admin sessions. Use fictional contact details when submitting inquiries. No real supplier messages are sent.

## Verify

Backend: run `python -m pytest -q` from `services/api` using its environment. Frontend: run `npm run build` from `apps/web`; lint is included. Run `node tests/proxy-contract.mjs` there for isolated proxy checks. With services running, execute `npm run test:e2e` and `node apps/web/tests/feature-smoke.mjs` at the repository root.

The complete executed scope and remaining boundaries are in `IMPLEMENTATION_STATUS.md`. Do not equate local success with production hardening or a hosted marketplace.
