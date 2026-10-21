# LavishCars marketplace — start here

Prepared by **Ayman Lakhnati** after the technical assessment. Independent concept, developed with AI assistance. All business records and rates are synthetic.

**[Review website](https://lavishcars-ayman-showcase.jocund-larch-4775.chatgpt.site)** · **[Public code](https://github.com/AymanLakhnati/lavishcars-ai-marketplace-showcase)**

## Review in five minutes

1. Watch the [4:35 product film](https://lavishcars-ayman-showcase.jocund-larch-4775.chatgpt.site/#walkthrough). It combines verified UI captures, explanatory graphics and fresh local API checks. Captured UI states are labeled; this is an edited evidence walkthrough, not a continuous live recording. Narration is synthetic.
2. Read the root README for reproducible setup. The essential workflow is supplier → draft → review → public offer → persisted inquiry.
3. Inspect `services/api/app/catalog.py` for shared public eligibility, `security.py` for authentication/ownership, and `main.py` for lifecycle and inquiry persistence.
4. Inspect `concierge.py`, `recommendations.py`, `provider.py` and `image_quality.py` for assistance and its limits. The no-key paths work; a real external-model call remains unverified.
5. Read `docs/DATABASE.md`, `docs/ARCHITECTURE.md` and `docs/IMPLEMENTATION_STATUS.md`. Tests cover core business boundaries rather than merely showing dashboards.

## Review evidence

- 22 backend tests passed, with SQLite foreign keys enforced in isolated fixtures.
- Four main browser scenarios and seven extended UI checks passed against the local production storefront and PostgreSQL.
- Five proxy contract checks, production build and dedicated lint passed.
- A real local WordPress installation rendered API catalog offers and respected supplier suspension/restoration.
- Fresh recording evidence verifies concierge records, preference scoring, supplier suggestions, image warnings/duplicates, actual insights and a new approval-to-inquiry path.

The latest verification report states the scope and remaining limitations. Remote CI has failed before jobs start; the public review presentation is deployed, while full application hosting remains unverified. There are no payments, payouts, reservation guarantees or real supplier notifications.

## Source layout

| Folder | Responsibility |
|---|---|
| `apps/web` | Next.js storefront, concierge and supplier/admin portals |
| `services/api` | FastAPI, SQLAlchemy, Alembic, PostgreSQL and backend tests |
| `integrations/wordpress` | Thin public API catalog/routing bridge |
| `tests` | Browser workflow and local WordPress checks |
| `docs` | Architecture, data model, AI behavior, audit and roadmap |
| `showcase` | Narration, review guide and employer email draft |
| `scripts/demo` | Reproducible local evidence, narration and video tooling |

The employer source bundle excludes confidential assessment attachments, credentials, runtime databases, uploads, package caches and Git history. `MANIFEST.sha256` records included file hashes.
