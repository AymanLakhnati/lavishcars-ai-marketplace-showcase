# Requirements audit

Audit date: 21 October 2026. This is a source-to-code assessment, not a certification of full compliance or production readiness. The project delivers the central Type A marketplace workflow. It does **not** yet satisfy every requirement in the larger master prompt.

## Sources and meaning of status

- **PDF**: original case study (confidential source omitted), with searchable extracted text (confidential source omitted). Section references below follow its numbered sections. This is the authoritative business brief.
- **M**: master implementation prompt (confidential source omitted), numbered sections. It expands scope beyond the PDF, especially AI, infrastructure and UI detail.
- **D — Delivered**: implementation is present and the cited evidence supports the claim. This does not imply every edge case has been tested.
- **P — Partial**: some meaningful implementation exists, but a specified part or required verification is missing.
- **M — Missing**: not implemented in the reviewed snapshot.
- **X — Excluded**: explicitly outside Type A V1; absence is intentional.

Code paths are repository-relative. Execution evidence is recorded separately in [implementation status](IMPLEMENTATION_STATUS.md); code inspection alone is not a passing runtime test. Current development may change individual rows; update a row only after inspecting the final implementation and its verification.

The PDF says no code is required for the assessment and prohibits devices, AI and notes **during the written assessment**. Those are assessment conditions, not application requirements. This prototype should be presented separately after the assessment, with honest AI-assisted development attribution. It must not be represented as work completed under those assessment conditions.

## Business and architecture

| ID | Source | Requirement | Status | Evidence and precise boundary |
|---|---|---|---|---|
| B1 | PDF §1,3; M §3,13 | Supplier → listing → approval → discovery → inquiry | D | `services/api/app/main.py`; complete browser path plus backend workflow tests. |
| B2 | PDF §3; M §3 | No checkout, payouts, P2P hosting, claims or transactional booking | X | Inquiry and CRM only. `booked` is manually recorded, not a reservation. |
| B3 | PDF §2,8; M §3,11 | Theme-independent marketplace authority | D | FastAPI/SQLAlchemy own records; WordPress adapter fetches public API. |
| B4 | PDF §2; M §11 | WordPress retains public content and eventual vehicle pages | P | Existing live site untouched; production architecture documented. Demo details run in Next.js, not WordPress. |
| B5 | M §4 | Next.js App Router/TypeScript frontend | D | `apps/web/app`, `apps/web/lib/api.ts`. |
| B6 | M §4 | Tailwind, shadcn, Motion, React Hook Form/Zod recommendations | P | React/TypeScript and Lucide used; CSS/custom forms are implementation choices. Not every suggested library was adopted. |
| B7 | M §4,10 | FastAPI, Pydantic, SQLAlchemy, PostgreSQL, OpenAPI | D | `services/api/app`; `/docs`; browser workflow exercised PostgreSQL. |
| B8 | M §4,6 | Migration-managed relational persistence | D | Immutable Alembic initial revision; migration checks executed. Future upgrades still need rehearsals. |
| B9 | M §4 | Compose and environment configuration | P | `docker-compose.yml`, `.env.example`; local services verified separately, no claim of completed Docker runtime validation. |
| B10 | M §4,15 | Local upload storage with object-store extension path | P | Validated/re-encoded filesystem uploads exist; dedicated storage-provider abstraction/object storage is not complete. |
| B11 | PDF §9; M §15 | Credible growth path without premature microservices | P | Pagination/indexes/modular monolith documented; target traffic/scale unmeasured. |

## Supplier and administration

| ID | Source | Requirement | Status | Evidence and precise boundary |
|---|---|---|---|---|
| S1 | PDF §4; M §5B | Register and maintain company profile | D | `/auth/register`, `/supplier/profile`; frontend supplier portal. |
| S2 | PDF §4,7; M §5B | Submit licence/verification information | D | Licence number/status information and manual administrator verification decisions; no external licence verification or document service is claimed. |
| S3 | PDF §7; M §5B,6 | Specify locations served | D | Normalized supplier_locations with authenticated GET/PUT service-area editor; listing writes enforce served cities. |
| S4 | PDF §4; M §5B | Add/edit specifications and separate prices | D | Listing editor and backend input models; brand/model/city consistency checks. |
| S5 | PDF §4; M §5B | Upload/reorder JPG/PNG/WebP; max 10, 8 MB each | D | Supplier editor ordering and upload endpoint; decoding/re-encoding and supplier-scoped paths. |
| S6 | PDF §5; M §5B,6 | Draft/review/publish with rejection reasons | D | Backend lifecycle transitions; admin-only approval and reason validation. |
| S7 | PDF §4; M §5B | Pause/remove own offers | D | Pause/archive actions preserve records; archive is the chosen removal behavior. |
| S8 | PDF §4; M §5D | Supplier sees/manages own leads only | D | Authenticated supplier-derived ownership and status update routes; isolation tests. |
| S9 | PDF §4; M §6 | Multiple authorized users per supplier | D | Normalized supplier_users; owner creates colleague accounts, member access stays within the supplier; no email invitation transport or custom granular roles. |
| S10 | PDF §5; M §5C | Approve/reject suppliers and listings | D | Admin endpoints and moderation interface. |
| S11 | PDF §5; M §5C,6 | Suspend supplier; independently hide offer | D | Supplier status and `admin_hidden`; shared public query excludes both. |
| S12 | PDF §5; M §5C | Edit or moderate offers administratively | D | Admin listing edit API and shared editor now present, with audit and archived-record restrictions; final runtime checks tracked separately. |
| S13 | PDF §5; M §5C,6 | Manage countries/cities/brands/models/categories | D | `taxonomy.py` and admin Taxonomy tab implement create/edit, parent/brand validation, cycle prevention and audit. Deletion intentionally absent; list capped at 1,000 rows. |
| S14 | M §5C,10 | Audit critical moderation changes | D | `audit_logs`, admin audit API/UI. Not an exhaustive immutable enterprise audit system. |
| S15 | M §5C | Admin provisioned outside public registration | D | Controlled development seed; extra registration role fields rejected. |
| S16 | M §6 | Material changes require renewed review | D | Published listing edits become pending; approved supplier company/licence changes become pending. |

## Customer, catalog and inquiries

| ID | Source | Requirement | Status | Evidence and precise boundary |
|---|---|---|---|---|
| C1 | PDF §6; M §5A,8 | Homepage, market discovery, responsive navigation | D | Home/fleet/detail/concierge routes and desktop/mobile screenshots. |
| C2 | PDF §6; M §5A | Country/city/brand/model/category search | D | Country/city/brand/model/category/type controls in fleet URL and API; model and location options load from reference endpoints. |
| C3 | M §5A | Price, transmission, seats and feature filters | D | Fleet exposes min/max price, transmission, seats and feature constraints, with API enforcement. |
| C4 | M §5A | Daily/weekly/monthly search periods | D | Catalog API and fleet period selector now filter/sort the selected stored rate; no inferred period multiplication. Concierge remains daily-budget oriented. |
| C5 | M §5A | Sorting, pagination and URL-based filters | D | Fleet URL parameters, API bounded pages; price/year sort and stable default listing-ID order. |
| C6 | M §5A,8 | Gallery, prices/currency, deposit, mileage, seats/features | D | `/fleet/[slug]`, listing serialization; optional values depend on stored offer. |
| C7 | M §5A | Trim and related vehicles | D | Dedicated trim/vehicle_type fields, editable supplier/admin forms, and related offers from the eligible catalog. |
| C8 | M §5A,6 | Only eligible offers public | D | `catalog.public_query()` reused by catalog/detail/concierge/lead creation. |
| C9 | PDF §6,7; M §5D | Structured inquiry with listing/supplier/location/contact/dates | D | Lead model/API and functioning detail form; supplier derived server-side. |
| C10 | M §5D | CRM new/contacted/quoted/booked/lost | D | Validated supplier/admin status changes. |
| C11 | M §5D,10 | Save before notification; survive delivery failure | D | Atomic lead/outbox commit; injected retry helper and failure test. No real delivery transport/worker. |
| C12 | M §5D | User-initiated WhatsApp option | D | Saved-inquiry WhatsApp share link opens recipient selection with a synthetic reference; no real company number or automatic send. |
| C13 | M §8 | Empty/loading/error, keyboard/focus/accessibility | P | States/labels/focus styles present; no comprehensive WCAG or assistive-technology audit. |
| C14 | M §8,12 | Clearly synthetic, licensed/local imagery | D | Local original SVG vehicle artwork and prototype labels; actual inventory/photography is not claimed. |

## Data and security

| ID | Source | Requirement | Status | Evidence and precise boundary |
|---|---|---|---|---|
| D1 | PDF §7; M §6 | Supplier/listing/brand/model/location/category/lead records | D | SQLAlchemy entities and foreign keys in `app/models.py`. |
| D2 | M §6 | `supplier_users`, `supplier_locations`, `listing_categories`, `listing_images` normalized tables | D | Migration 0003 creates/backfills supplier_users, supplier_locations, listing_categories and listing_images; canonical reads and writes use associations. |
| D3 | PDF §7; M §6 | Hierarchical locations, future areas/airports | D | Parent FK and taxonomy editor support country/state/city/area/airport; cycle and parent-kind validation; structural changes with dependents are rejected. |
| D4 | M §6 | Precise money, explicit currencies, independent periods | D | Numeric columns and Decimal input; AED/USD, no conversion; no runtime multiplication for period rates. |
| D5 | M §6,12 | Active/future markets and representative lifecycle seeds | D | Seed Dubai/Houston plus inactive expansion markets, published/pending/rejected/paused listings. |
| D6 | M §10 | Password/session/role/ownership controls | D | Salted scrypt, hashed expiring tokens, role dependencies, supplier record checks. Production hardening still required. |
| D7 | M §10 | Validation, parameterized access, escaping | D | Pydantic/SQLAlchemy/React escaping; WordPress uses escaped output. |
| D8 | M §10 | Upload validation and private verification/lead boundaries | D | Re-encoded bounded images, ownership checks; private records behind role/ownership checks. |
| D9 | M §10 | CORS, rate limiting, environment secrets | P | Origin allowlist and process-local sensitive-route limiter; shared anti-abuse and production secret handling pending. |
| D10 | M §10 | CSRF where cookie authentication requires it | D | Authorization bearer header used; authentication is not cookie-based. localStorage token/XSS trade-off documented. |
| D11 | M §15 | Efficient bounded query/search behavior | P | Indexes and page caps exist; serialization/large taxonomy performance not load-tested. |

## AI and insight requirements

| ID | Source | Requirement | Status | Evidence and precise boundary |
|---|---|---|---|---|
| A1 | M §7 feature 1 | Parse location/budget/duration/seats/category | D | Deterministic parser supports common phrases and number words; bounded language coverage. |
| A2 | M §7 feature 1 | Focused clarification, structured response | D | City/currency/budget clarifications; filter object and record-backed recommendation objects. |
| A3 | M §7 features 1–2 | Up to three actual eligible records and explanations | D | Public eligibility query, hard constraints, feature scoring and record-based cards. |
| A4 | M §7 feature 2 | Preference/occasion ranking with transparent weights | D | `/ai/recommendations` and explicit preference UI: hard constraints, +20 preferred-category and +10 editorial occasion fit, price/ID ties; 500-candidate bound. Not learned personalization. |
| A5 | M §4,7 | Configurable OpenAI-compatible provider | P | `provider.py` implements HTTPS chat-completions extraction via AI_API_KEY/AI_MODEL/AI_BASE_URL. Real external-provider invocation not yet verified; no credentials assumed. |
| A6 | M §7 | Works with no paid API; core independent of AI | D | Rules-based path and normal fleet/inquiry routes. |
| A7 | M §7 | No invented prices/availability/booking/approval authority | D | Facts from records; no reservation function; raw model decisions cannot publish. |
| A8 | M §7 feature 3 | Supplier extraction + editable explicit application | D | Listing assistant endpoint and preview/apply/save separation. Unknown details identified. |
| A9 | M §7 feature 4 | Counts/leads/status insights from actual data | D | Aggregate endpoint and supplier overview. |
| A10 | M §7 feature 4 | Views, category interest, per-listing conversion and generated summaries | D | Detail API event tracking, most-viewed offers, primary-category inquiry counts and raw inquiries per 100 detail requests. Repeats/bots/demo requests count; this is descriptive, not unique-visitor conversion attribution. |
| A11 | M §7 feature 5 | Optional image quality/duplicate/vehicle checks | P | Local resolution/brightness/edge-detail/hash duplicate warnings and a documented cover score work. Semantic vehicle detection is not implemented; this optional stretch scope is explicitly bounded. |
| A12 | M §7 | Provider-failure fallback, schema validation, PII minimization | P | Adapter schema-validates output, limits outbound tokens, scrubs common contacts/secrets and falls back on errors. Finite sanitization is not a complete PII detector; real-provider behavior remains unverified. |

## WordPress, testing and delivery

| ID | Source | Requirement | Status | Evidence and precise boundary |
|---|---|---|---|---|
| W1 | M §11 | Public catalog/location/filter adapter | D | PHP lint, real local WordPress plugin activation, filtered page rendering, detail links, supplier suspension and restoration verified. Company theme/production SEO rollout remains unverified. |
| W2 | M §11 | Detail/inquiry routing bridge | D | Adapter links to actual `/fleet/{slug}` detail/inquiry route; no duplicate authority. |
| W3 | PDF §2; M §11 | Production WordPress pages/permalinks/SEO | M | Documented rollout, no actual deployment. |
| T1 | M §13–14 | Core customer/supplier/admin end-to-end tests | D | Backend and Playwright critical path verified; see exact counts in status report. |
| T2 | M §13–14 | Isolation, suspension, failure, fallback tests | D | Representative backend cases; not exhaustive adversarial testing. |
| T3 | M §14–15 | Type checks/build, accessibility/load/security QA | P | Build/TS/browser/audit checks executed; complete accessibility/load/security assessment absent. |
| T4 | M §12,17 | Reproducible seed, docs, demo accounts and script | D | Seed, README, architecture/database/AI/status/roadmap/demo docs. |
| T5 | M §17; user delivery request | Reviewer deployment and recording URL | P | Working local runtime; external preview deployment and URL must be independently verified before sharing. |
| T6 | M §18–19 | Fully implemented master prompt / production readiness | P | Useful tested vertical slice; explicit omissions above preclude either claim. |

## Defensible employer claim

“This is an AI-assisted, unofficial prototype demonstrating the core marketplace workflow and explainable recommendations grounded in approved inventory. It respects WordPress as the intended content layer. I can demonstrate the implemented flows, explain the tests and trade-offs, and show a documented path for the remaining work.”

Do not say “100% compliant”, “all AI capabilities complete”, “production-ready”, “deployed WordPress integration”, “verified live inventory”, or “independently coded without assistance”. Actual employer evaluation and hiring decisions cannot be guaranteed by the prototype.
