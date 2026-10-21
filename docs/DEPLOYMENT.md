# Deployment runbook and status

Status on 21 October 2026: the local PostgreSQL/API/Next.js demo is verified. No externally shareable deployment URL has been verified. Two dedicated Vercel projects are linked in workspace `aymans-projects-0dcb7412`: API `lavishcars-marketplace-api` and web `lavishcars-ai-marketplace`.

## Current account blocker

The authenticated Vercel CLI returns `integration_terms_acceptance_required` when provisioning the Neon free database. The required workspace page is:

https://vercel.com/aymans-projects-0dcb7412/~/integrations/accept-terms/neon?source=cli

Browser access to vercel.com is blocked by a saved user permission, and Chrome is not exposed to the browser tool. Importing browser passwords does not grant website permission or accept integration terms. The agent must not bypass this gate. The account owner can remove vercel.com from the browser blocklist and connect the signed-in browser, or complete the acceptance page directly. Any final binding-terms action requires action-time confirmation.

No temporary database, localhost tunnel or frontend-only preview is represented as a durable full deployment.

## After account acceptance

1. Use the authenticated Vercel CLI in the correct workspace. Provision the dedicated free Neon resource. Do not repurpose databases belonging to unrelated projects.
2. Link/connect its database environment only to the API project. Keep connection strings server-side and out of shell output, Git, screenshots and recordings.
3. Set API environment values: `DATABASE_URL` (managed PostgreSQL), `APP_ENV=demo`, `UPLOAD_STORAGE=database`, `DB_NULL_POOL=1`, and an explicit `CORS_ORIGINS` allowlist. Choose a unique `DEMO_PASSWORD` before the first seed and share reviewer access privately. The production web build does not prefill a password.
4. Apply migrations with the API's Python environment: `alembic upgrade head`, then `alembic check`. Run `python -m app.seed` only against the dedicated fictional demo database. Demo seeding refuses `APP_ENV=production`.
5. Deploy from `services/api` using `vercel deploy --prod`. Its `pyproject.toml` points to `app.main:app`, declares runtime dependencies and requires Python 3.12+. Confirm the actual API URL with `/health` and a public catalog request.
6. Set the web project's build variable `NEXT_PUBLIC_API_URL=/api/v1` and server runtime `API_INTERNAL_ORIGIN=https://ACTUAL_API_ORIGIN`. Deploy from `apps/web`. The fixed-origin server proxy forwards authorized API requests and image reads without exposing the database URL.
7. Verify the hosted customer/supplier/admin flow and image retrieval after another API invocation. Run browser tests with `TEST_WEB_URL` and `TEST_API_URL` targeting the actual demo. Inspect the responsive layout and service errors on that URL before sharing it.
8. Record the verified URLs and deployment IDs here, update the employer guide and push documentation. Review how access will be granted to the employer; a private GitHub repository requires explicit reviewer access.

For normal local development, `NEXT_PUBLIC_API_URL` defaults to the direct localhost API. The hosted configuration uses the same-origin proxy. Original images up to 8 MB are accepted by the UI; larger files are optimized before upload to stay below serverless request limits, and the API validates/re-encodes again.

## AI and notification deployment policy

All showcase flows work without a paid model. Optional `AI_API_KEY`, `AI_MODEL` and HTTPS `AI_BASE_URL` belong only on the API. Do not claim a real external-model invocation until verified with authorized credentials. Supplier note extraction, summaries and image checks remain deterministic. The outbox retains inquiries without sending real supplier messages; deploy a transport/worker only as a separate deliberate step.

## Platform references

- [Vercel FastAPI deployment](https://vercel.com/docs/frameworks/backend/fastapi)
- [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel integration marketplace terms](https://vercel.com/legal/integration-marketplace-end-users-addendum)
- [Neon terms](https://neon.tech/terms-of-service)
