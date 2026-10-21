# LavishCars AI Marketplace

An unofficial, local concept prototype of a multi-supplier luxury vehicle listings
marketplace. All inventory, supplier identities and rates are synthetic.

**Supplier → draft listing → review → publication → customer inquiry.**
The concierge searches the same approved database inventory and returns up to three
matching vehicles. Intended dates are quote preferences, never a reservation.

![Marketplace homepage](docs/screenshots/home-desktop.png)

For a company review, begin with the [reviewer guide](docs/REVIEWER_GUIDE.md)
and the [employer recording guide](docs/EMPLOYER_PRESENTATION.md).

Verified locally: **22 backend tests, 4 browser scenarios, a successful production
frontend build, and zero reported production npm vulnerabilities**. The browser
suite ran against PostgreSQL. See the exact scope in the status report.

## Start with Docker

Requires Docker Compose. From this repository:

```sh
cp .env.example .env
docker compose up --build
```

Open http://localhost:3000. API documentation: http://localhost:8000/docs.
The stack runs PostgreSQL, migrations, an idempotent demo seed, FastAPI and Next.js.
Compose is a **local demonstration configuration**, with ports bound to loopback.
Do not expose its default credentials or seeded administrator to the Internet.

## Start without Docker

Requires Python 3.12+ and Node 22+. Each terminal starts at this repository.

For PostgreSQL without Docker, first run the optional local database in its own
terminal. This downloads no system service and keeps data under `.runtime/`:

```sh
npm ci
npm run db:local
```

Then set the API terminal's `DATABASE_URL` before migration:

```powershell
# PowerShell
$env:DATABASE_URL = "postgresql+psycopg://lavish:lavish_local_only@127.0.0.1:54329/lavish"
```

```sh
# macOS/Linux
export DATABASE_URL='postgresql+psycopg://lavish:lavish_local_only@127.0.0.1:54329/lavish'
```

API:

```sh
cd services/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
# Optional: set DATABASE_URL to your PostgreSQL SQLAlchemy connection URL.
# Without it, development uses a persistent local SQLite database.
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Web, in another terminal:

```sh
cd apps/web
npm ci
npm run dev
```

`NEXT_PUBLIC_API_URL` defaults to `http://localhost:8000/api/v1`. Set it before
building if you run the API elsewhere. Do not put database credentials in frontend
environment variables.

## Demo accounts

The development seed provisions these accounts using `DEMO_PASSWORD`
(default: `DemoDrive!2026`):

| Account | Role |
| --- | --- |
| `admin@lavish.demo` | Administrator |
| `supplier@lavish.demo` | Approved supplier |
| `pending@lavish.demo` | Supplier awaiting approval |
| `houston@lavish.demo` | Independent Houston supplier |

Public registration creates supplier accounts only. Use synthetic contact details
for inquiries. Notifications are retained locally; they do not contact LavishCars.

## Verification

Backend:

```sh
cd services/api
python -m pytest -q
```

Frontend:

```sh
cd apps/web
npm run build
```

Browser scenarios, with the API and storefront running:

```sh
npm ci
npx playwright install chromium
npm run test:e2e
```

CI runs backend tests, migration checks, a production web build, and the browser
suite with PostgreSQL. Local verification and remote CI results are reported
separately.

See [implementation status](docs/IMPLEMENTATION_STATUS.md) for actual executed
checks, limitations and outstanding requirements, and
[the demonstration script](docs/DEMO_SCRIPT.md) for a stakeholder walkthrough.

## Design and sources

- [Requirements audit](docs/REQUIREMENTS_AUDIT.md)
- [Employer presentation and recording roadmap](docs/EMPLOYER_PRESENTATION.md)
- [Deployment runbook and current status](docs/DEPLOYMENT.md)

- [Architecture](docs/ARCHITECTURE.md)
- [Database](docs/DATABASE.md)
- [AI behavior and guardrails](docs/AI_DESIGN.md)
- [Roadmap](docs/ROADMAP.md)
- [Discovery and source references](docs/DISCOVERY.md)
- [Original master prompt](docs/references/MASTER_PROMPT.md)
- [Original case study](docs/references/case-study.pdf)

The original assessment is confidential candidate material. Keep this repository
private unless its owner authorizes distribution.

WordPress remains the proposed production content and SEO layer. The adapter under
`integrations/wordpress` reads the public API and routes to the demonstration
storefront. The Next.js app is not a deployed replacement for the live company site.
