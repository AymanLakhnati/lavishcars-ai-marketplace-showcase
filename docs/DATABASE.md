# Database and business rules

The implemented SQLAlchemy schema is in `services/api/app/models.py`. PostgreSQL is the deployment target; isolated SQLite databases support tests. Alembic revisions `0001`–`0003` define and migrate the schema explicitly.

| Tables | Responsibility |
|---|---|
| `users`, `sessions` | Unique email, scrypt password hash, role, hashed expiring bearer tokens. |
| `suppliers` | Company/contact/licence fields, review status, separate active flag and rejection reason. |
| `supplier_users` | Unique supplier membership per user, owner/member role. Owners can create colleague accounts; members cannot administer the team. |
| `supplier_locations` | Multiple served cities. Listing writes enforce these areas; published offers prevent removal of their served city. |
| `locations` | Country/state/city/area/airport hierarchy, active flags. Cycles and invalid parent kinds are rejected. |
| `brands`, `models`, `categories` | Administrator-managed reference data. Each model belongs to a brand. |
| `listings` | Supplier/model/location/primary category; trim/type/specifications, precise independent rental rates, lifecycle and visibility. |
| `listing_categories` | Multiple categories per offer, including the primary category. Public category filters use this association. |
| `listing_images` | Canonical ordered image paths per offer. |
| `uploads` | Supplier-owned re-encoded image bytes, hash and media type; durable database delivery for serverless hosting. |
| `leads` | Listing/supplier/location, customer contact, dates, message, source, CRM status and timestamp. |
| `listing_views` | Detail API request events. Repeated, automated and demo requests count; these are not unique visitors. |
| `notification_outbox`, `audit_logs` | Durable notification attempts and critical administrative actions. |

The legacy user supplier FK and listing primary-category/image fields remain compatibility mirrors. Membership authorization and public category/image reads use normalized associations. Features remain a bounded JSON array. Revision `0003` backfills existing records rather than relying only on fresh seeds.

## Publication and ownership

Listings start as drafts. Submission requires a valid photo and sufficient description; only an administrator can approve a pending listing. Published edits require renewed review. Rejection records a reason; pause/archive preserve records, and archived listings cannot be edited.

Catalog, details, recommendations and inquiry creation share eligibility: published listing, approved and active supplier, no admin hide, and an active location hierarchy. Suspending a supplier or disabling an ancestor market removes public discovery without deleting records. Authenticated membership determines private ownership. The inquiry stores its responsible supplier/location at creation.

`booked` is a manually recorded CRM outcome. There is no reservation ledger, availability guarantee, payment or payout.

## Money, indexing and migration evidence

Prices/deposits use `Numeric(12,2)` and Decimal input. AED/USD are explicit; no exchange-rate conversion is implemented. Weekly/monthly rates are stored independently. New market currency policy requires deliberate configuration before expanding beyond the supported demonstration markets.

Discovery/status/location/currency/price, unique slug, supplier references, memberships, image hashes and detail-event references have indexes. Bounded pagination and candidate limits avoid unbounded catalog loading; real query plans and load measurements are needed before claiming a scale target.

Fresh SQLite upgrade → schema check → downgrade → upgrade passed. PostgreSQL upgrade and schema drift check passed against the local demo database. Backup/restore, concurrent migrations and production-sized upgrades still require rehearsal.

## Inquiry durability and limits

Lead and outbox event commit atomically before success. `app/notifications.py` provides bounded retries with an injected transport and persists attempts/failures. No real supplier messages are sent. A production worker needs backoff, locking, idempotent delivery and monitoring.

Team creation demonstrates account provisioning rather than email invitations. Licence documents, granular custom roles, retention/deletion policy, storage lifecycle cleanup and recovery procedures remain separate work.
