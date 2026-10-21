# LavishCars marketplace concept — reviewer guide

This demonstration explores the company's Type A marketplace case study:
licensed supplier registration, controlled listing publication and customer leads.
It is an independent concept with synthetic inventory and illustrative rates.

## Run and inspect

Use `docker compose up --build` from the repository, or follow the root README for
Python/Node setup and an optional local PostgreSQL runtime. Docker itself was not
available on the development machine; the directly launched application and
PostgreSQL were used for verification.

| Review surface | Local address | What to inspect |
| --- | --- | --- |
| Customer storefront | http://localhost:3000 | Editorial homepage, locations and approved catalog |
| Concierge | http://localhost:3000/concierge | Real catalog matches, prices and reasons |
| Supplier workspace | http://localhost:3000/supplier | Drafts, photo uploads, submission and leads |
| Administration | http://localhost:3000/admin | Supplier/listing moderation and inquiry statuses |
| Interactive API | http://localhost:8000/docs | Versioned API contracts and authorization |

Demo password: `DemoDrive!2026`, unless changed with `DEMO_PASSWORD` before seeding.
Supplier: `supplier@lavish.demo`. Administrator: `admin@lavish.demo`.
Use a separate browser profile for the admin, or sign out before switching roles.

## The showcase moment

Enter this request in the concierge:

> I'm in Dubai for four days, looking for a luxury SUV under AED 1,000 per day.

The original seed contains three eligible matches: Cadillac Escalade at AED 850,
Range Rover Sport at AED 900, and Mercedes-Benz G-Class at AED 990 per day. These
are synthetic demonstration rates. The service retrieves actual eligible database
records and returns up to three matches; moderation or changed inventory can alter
the result. Open a card and submit an inquiry using fictional contact details.
The confirmation includes a persisted reference that authorized users can inspect.

For the full six-minute sequence, use `DEMO_SCRIPT.md`.

## Technical decisions worth discussing

- FastAPI and the relational database own supplier, listing, moderation and lead
  records. Public eligibility and supplier ownership are enforced server-side.
- WordPress remains the proposed marketing, SEO and public publishing layer. A
  small API-consuming plugin illustrates the integration boundary.
- The concierge and supplier assistant use explicit, testable interpretation rules
  and work without a paid provider. They never create a reservation or invent
  inventory. An optional configurable extraction adapter has mock-based failure/schema tests; a real external-model call remains unverified.
- Leads and outbox events are saved together. Notification failure cannot erase a
  saved inquiry. The demonstration does not send real supplier messages.

## Verification and limits

The automated evidence covers the primary supplier → photo upload → submission →
admin approval → public search → inquiry path, plus permissions, suspension,
validation, notification failure and recommendation constraints.

Screenshots of the [homepage](screenshots/home-desktop.png),
[concierge](screenshots/concierge-desktop.png),
[supplier workspace](screenshots/supplier-desktop.png) and
[admin console](screenshots/admin-desktop.png) are included for quick review.

See `IMPLEMENTATION_STATUS.md` for exact checks and remaining scope. In particular,
the WordPress plugin has been tested locally, including suspension visibility. Production hosting, real notification delivery and live provider verification remain outstanding. Taxonomy, service areas, team accounts and normalized associations are implemented. The homepage uses labeled AI-generated concept artwork;
vehicle cards without supplier photos use original illustrations.

The repository is private because it includes the original confidential assessment.
The owner can grant reviewer access or share the source archive directly. A private
GitHub URL requires access; localhost is only reachable on the machine running it.
