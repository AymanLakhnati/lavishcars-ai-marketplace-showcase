# LavishCars AI Marketplace

**Independent concept by Ayman Lakhnati. AI-assisted development. Synthetic data.**

Start with `REVIEW_START_HERE.md` and the narrated demonstration supplied separately. This repository demonstrates a Type A listings marketplace:

**Supplier → listing → administrator approval → discovery → persisted inquiry.**

Implemented assistance includes database-grounded concierge results, transparent preference ranking, editable supplier listing suggestions, scoped factual insights and local photo-quality/duplicate checks. The no-key paths work without a paid model. An optional external-provider adapter is implemented; a live provider call is unverified.

## Run locally

Requires Docker Compose:

```sh
cp .env.example .env
docker compose up --build
```

Storefront: http://localhost:3000 · API: http://localhost:8000/docs

Compose is a local demo configuration. Docker runtime was unavailable on the development machine; directly launched PostgreSQL/API/Next.js were used for verification. Alternative Python/Node commands are in `docs/LOCAL_SETUP.md`.

Local seeded users: `supplier@lavish.demo`, `admin@lavish.demo`, `pending@lavish.demo`, `houston@lavish.demo`. The local default password is `DemoDrive!2026`, configurable through `DEMO_PASSWORD` before first seeding. Do not expose these defaults publicly. Use only fictional inquiry details.

## Verify

```sh
cd services/api
python -m pip install -r requirements.txt
python -m pytest -q
```

```sh
cd apps/web
npm ci
npm run build
node tests/proxy-contract.mjs
```

With local API/storefront running, execute from the root:

```sh
npm ci
npx playwright install chromium
npm run test:e2e
node apps/web/tests/feature-smoke.mjs
```

Read `docs/IMPLEMENTATION_STATUS.md` for exact executed results and limits. Remote CI has a startup failure; local passing checks are reported separately.

## Inspect the design

- `docs/ARCHITECTURE.md`: system ownership, WordPress and security boundaries.
- `docs/DATABASE.md`: normalized schema, money, lifecycle and migrations.
- `docs/AI_DESIGN.md`: parsing, ranking, provider fallback and image heuristics.
- `docs/REQUIREMENTS_AUDIT.md`: implemented scope and remaining boundaries.
- `docs/ROADMAP.md`: production rollout and operational priorities.

WordPress remains the intended marketing/SEO/public content layer; Next.js is the demonstration storefront. The locally tested bridge consumes the public API. Production WordPress routes, hosting, notification workers, storage/operational hardening and live model verification remain separate work. Payments, payouts and transactional booking are intentionally outside Type A V1.

Confidential assessment documents and the original master prompt are omitted from this review distribution.
