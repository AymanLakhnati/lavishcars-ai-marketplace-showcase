# Discovery and decisions

Reviewed 20 October 2026.

The supplied PDF is preserved in `references/case-study.pdf`; extracted text is in
`references/case-study.txt`. The implementation brief is preserved separately in
`references/MASTER_PROMPT.md`. The PDF's assessment-day restrictions describe the
assessment itself; they are not application behavior or instructions for this build.
The user explicitly requested a working application.

## Authoritative scope

Supplier registration → listing → administrator approval → customer discovery →
persisted inquiry. This is a Type A listing marketplace. No checkout, payments,
supplier payouts, insurance, or transactional reservations.

WordPress remains the intended production publishing and SEO layer. FastAPI is
the single system of record. Next.js demonstrates the proposed customer experience.

## Public references

Read-only inspection of:

- https://lavishcars.com/
- https://lavishcars.com/our-story/
- https://lavishcars.com/uae/dubai/
- https://lavishcars.com/uae/dubai/fleet/
- https://lavishcars.com/usa/houston/fleet/
- https://lavishcars.com/list-your-car/
- https://lavishcars.com/contact-us/
- https://lavishcars.com/privacy-policy/

The homepage organizes discovery around Dubai and Houston and emphasizes personal
service and pricing transparency. The prototype uses these market and trust themes
without copying live customer records, claims, supplier inventory, or photographs.
No live forms were submitted.

## Implementation order

1. Persistent schema, server authorization, listing lifecycle and lead reliability.
2. Customer storefront, supplier workspace and moderation console.
3. Database-grounded concierge with deterministic interpretation and explanations.
4. Supplier note assistance, aggregates and thin WordPress adapter.
5. Integration tests, browser checks, launch instructions and an honest status report.

## Local environment

Windows host with Node 22 and bundled Python 3.12. Docker and PostgreSQL were not
initially installed. Compose targets PostgreSQL; a SQLite development fallback
allows the application and tests to run without provisioning a machine service.
Runtime data, uploads and credentials are excluded from Git.
