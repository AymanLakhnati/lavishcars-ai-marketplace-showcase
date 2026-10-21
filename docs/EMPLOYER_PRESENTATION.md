# Employer presentation and recording guide

Use this after the written assessment as an optional demonstration, separate from the assessment itself. The supplied assessment prohibits AI/tools/notes during the written session. This project was developed with AI assistance; do not imply otherwise. The goal is to show business understanding, engineering judgment and an ability to explain the implementation, not to promise a hiring outcome.

## Recording access and preparation

- **Verified local storefront:** `http://localhost:3000` while the documented services are running. API health: `http://localhost:8000/health`; API documentation: `http://localhost:8000/docs`.
- **Externally shareable preview:** not yet verified in this document. Replace this line only with a URL confirmed by the deployment owner; do not send `localhost` as an employer-accessible link.
- **Credentials:** local seed uses `supplier@lavish.demo`, `admin@lavish.demo`, `pending@lavish.demo` and `houston@lavish.demo`; password comes from `DEMO_PASSWORD` (local default `DemoDrive!2026`). Hosted credentials may differ. Do not expose an administrator password in the recording, follow-up email or public repository.
- Open a normal browser profile for supplier actions and a separate private/profile window for administrator actions. Shared localStorage sessions within one profile can otherwise switch roles unexpectedly.
- Rehearse the exact seed and query. Keep three approved Dubai SUVs below AED 1,000 eligible for the opening concierge scene. Confirm pending/suspended/hidden offers do not appear.
- Prepare one permitted JPG/PNG/WebP demo vehicle image, under 8 MB, for the upload. Use synthetic customer data: `Demo Visitor`, `demo@example.com`, `+10000000000`. Do not use real supplier/client records.
- Record the browser window at 1920×1080 where possible, with readable text and no credential tabs, notifications or personal account UI visible. A clean 6–7 minute take is enough; do not speed through proof of publication and inquiry persistence.
- Read [requirements audit](REQUIREMENTS_AUDIT.md), [AI design](AI_DESIGN.md) and [implementation status](IMPLEMENTATION_STATUS.md) before recording. Use the actual current test report; never invent test counts or availability.

## Exact spoken script and shot list — approximately 6:40

Use the quoted narration naturally. Actions are not spoken. If a planned feature is unavailable in the actual running build, omit it and acknowledge the limit rather than editing in a simulated success.

### 0:00–0:40 — Business understanding

**Screen:** Homepage, then destination navigation.

> “After studying the case, I built this unofficial concept to demonstrate the core business workflow: licensed supplier, vehicle listing, LavishCars approval, customer discovery and inquiry. I used AI coding assistance during development, and I am presenting it separately from the written assessment. I can walk through the implementation, the tests and the trade-offs. The inventory and rates shown here are synthetic. This is a listings marketplace: there is no checkout, payment or confirmed reservation.”

### 0:40–1:45 — The showcase: grounded discovery

**Screen:** `/concierge`. Enter: `I'm in Dubai for four days, looking for a luxury SUV under AED 1,000 per day.` Pause on the three results, prices and explanations.

> “The visitor can describe a trip instead of learning the filter interface. Here, the request is Dubai, an SUV and a daily budget below one thousand dirhams. The result cards come from approved records in the database. The system checks supplier eligibility and listing visibility before it ranks anything. The explanations show why the records match; they do not invent a confidence percentage. The no-key interpretation path is deterministic, so the demonstration works without a paid model. Four days is a trip preference, not a promise that the vehicle is available. Availability and final terms still require supplier confirmation.”

**Action:** Click a result. Point to the same model and price on its detail page. Do not describe a provider-backed mode unless the running interface actually reports it and its invocation was verified.

### 1:45–2:30 — From interest to a saved lead

**Screen:** Vehicle detail and quote form. Submit synthetic details, then show confirmation.

> “The detail page makes the currency, rental price and vehicle information explicit. A request becomes a structured inquiry associated with this offer, its supplier and location. The backend determines that association; the visitor cannot choose an arbitrary supplier identity. The inquiry is persisted before any notification attempt. This confirmation means the request was saved. It does not mean a booking or payment has occurred.”

**Action:** In the separate authorized console, show the inquiry record briefly if time permits. Keep the confirmation and record name consistent.

### 2:30–3:45 — Supplier productivity with reviewable assistance

**Screen:** Supplier workspace → Add vehicle. Enter: `2026 Range Rover Sport SUV, automatic, five seats, Dubai, panoramic roof, AED 900 a day.` Preview, apply, review fields, upload image, save and submit.

> “Suppliers have a dedicated workspace rather than the standard WordPress admin. The listing assistant turns rough notes into suggested fields. It shows missing information, and the supplier must review and apply the suggestions. Applying does not publish or even save the offer. I still confirm the details, add a vehicle image and submit the listing for review. Uploads are validated and stored under the supplier identity. At this point the offer is pending, and the customer catalog must not show it.”

**Action:** Briefly show the pending status or a private-before-approval check. If filling a form takes longer, reduce introductory narration rather than implying an unperformed upload.

### 3:45–4:40 — Approval is a real boundary

**Screen:** Separate admin session → pending listing → approve → return to public fleet/new listing.

> “The administrator now reviews the offer and approves it. Publication is enforced by the API, not by hiding a button in the supplier screen. After approval, this offer is visible to customers because its supplier is also eligible. The same rule is reused for search, details, recommendations and inquiry creation. Hiding an offer or suspending its supplier removes it from those public paths without deleting the underlying business records. Material edits require renewed review.”

**Action:** Show the newly published record or its generated slug so it is distinguishable from the seed offer. Do not claim to have demonstrated suspension unless you actually perform it; the script explains its implemented rule.

### 4:40–5:30 — Respect the existing WordPress investment

**Screen:** Architecture diagram in `docs/ARCHITECTURE.md`, then the locally running WordPress catalog at `http://127.0.0.1:8088/?page_id=4` if available. Otherwise use its verification report.

> “The architecture preserves the WordPress strategy. WordPress remains the intended home for marketing, location pages and editorial content. The marketplace backend owns suppliers, offers, approval and inquiries independently of the theme. Next.js demonstrates the proposed experience. The WordPress bridge was activated and tested locally: it reads the API catalog and follows supplier suspension without storing a second vehicle database. Production WordPress vehicle pages and the full integration are still rollout work around existing URLs, SEO, caching and inquiry behavior.”

### 5:30–6:40 — Evidence, boundaries and value

**Screen:** `docs/IMPLEMENTATION_STATUS.md`, then `docs/REQUIREMENTS_AUDIT.md`. Show actual current passed checks and one partial requirement.

> “I prioritized a working vertical slice and tested the business boundaries. The verification report distinguishes backend tests, a production build and browser workflows against PostgreSQL. It also separates local verification from any hosted or WordPress verification. I would not call this fully compliant with the larger implementation prompt or production-ready: the audit identifies the remaining work explicitly. The value I wanted to demonstrate is practical: suppliers can submit offers, LavishCars controls publication, customers can find suitable vehicles, and inquiries become actionable records. The next step would be to agree on the smallest production scope and validate the WordPress integration in staging.”

> “I would be happy to explain any part of the data model, permission checks or recommendation pipeline, including where I would change the prototype for production.”

## Optional 30-second inserts

Use only after verifying the exact feature in the current build; do not extend the recording past seven minutes unless requested.

- **Insights:** Show actual listing/lead aggregates and describe only those recorded counts. Do not call them market-demand forecasts or proven conversion improvements.
- **Taxonomy:** Show an administrator editing a safe demonstration taxonomy record, then its effect on selection. Avoid deleting seeded records needed by the walkthrough.
- **Photo assistance:** Show actual quality warnings if implemented. Distinguish image statistics from semantic vehicle verification; no claim of detecting a vehicle, model or ownership without a verified classifier.
- **Provider mode:** Show the actual reported mode. A configurable adapter with mock tests is not evidence of a real paid-model call. Keep the fallback story clear.

## Technical questions to rehearse

Before recording, reserve 90 minutes: 20 minutes to trace the data model, 20 for authorization and publication rules, 20 for the concierge/ranking/fallback pipeline, 15 to rehearse the supplier/admin/inquiry sequence, and 15 for one timed take. Explain a choice in your own words before moving on. Your strongest differentiator is proving business rules and discussing trade-offs clearly.

| Question | Defensible answer |
|---|---|
| Why not implement everything in WordPress? | The case permits a separate backend. Centralizing marketplace records and permissions avoids coupling business state to a theme. WordPress can remain the publishing layer. A plugin-only implementation could also work, but this prototype chooses explicit API ownership. |
| Why Next.js if WordPress stays? | It demonstrates the experience and portals quickly. It is not an authorized production replacement. Production public routes require a deliberate WordPress/SEO rollout. |
| Is this a booking system? | No. Dates are inquiry preferences; `booked` is a manually recorded CRM outcome. There is no availability ledger, inventory lock, payment or reservation guarantee. |
| How do you prevent another supplier reading my leads? | Authentication establishes the supplier identity; every private listing/lead query scopes ownership server-side. Role and isolation tests exercise the boundary. Public records are deliberately separate. |
| What happens after suspension? | The shared public-eligibility rule excludes the supplier's offers. Data stays available to authorized administration; no destructive cleanup is needed. |
| What makes the AI trustworthy? | Interpretation produces constraints, while eligible database records supply facts. Ranking cannot publish offers or create bookings. Supported deterministic behavior remains available without a provider. The parser has documented limits; it is not general understanding. |
| What if a notification fails? | The lead and outbox record commit first. Failure remains retryable without losing the inquiry. A deployed worker/transport and delivery policy are additional operational work. |
| How does this scale? | Start with bounded queries, relational indexes and measurements. Address observed query bottlenecks, move uploads to object storage, and add caching with moderation invalidation. No unmeasured throughput claims. |
| How was AI used in development? | AI assisted coding, analysis and verification. I would distinguish generated assistance from my own understanding, explain the design decisions and demonstrate the running code. I would not claim unaided authorship. |
| What would you change before production? | Use the requirements audit to agree scope; harden sessions/secrets/abuse controls, review PII and retention, rehearse database recovery, integrate WordPress in staging and expand edge-case/accessibility testing. |

If you cannot explain a particular implementation, say “I would inspect that path before making a claim,” then inspect it. Do not memorize an answer that you cannot substantiate.

## Recording contingencies

| Situation | Response |
|---|---|
| Hosted URL fails | Use the verified local runtime for the recording and label it local. Do not imply the hosted link is working; repair/retest before sharing the link. |
| Provider disabled, unavailable or no API key | Demonstrate the deterministic mode and name it. Do not insert generated conversation footage. |
| Fewer than three matching offers | Check seed eligibility/status and query. Show the actual result count; do not invent cards. |
| Inquiry fails | Show the error, restore the API and repeat with synthetic data. Verify the saved CRM record instead of claiming a success banner means persistence. |
| Wrong role in another tab | Use distinct browser profiles/private sessions and log in again. Do not disable permissions to rescue the recording. |
| A feature in this script changed | Rehearse against the current build and adjust the narration to what it actually does. |

## Follow-up message — draft only, not sent

**Subject:** Follow-up: LavishCars marketplace concept and technical walkthrough

Hello [Name],

Thank you for the assessment and the opportunity to learn more about LavishCars. Separately from the written assessment, I developed an unofficial, AI-assisted concept to demonstrate the supplier-to-listing-to-approval-to-inquiry workflow and explainable recommendations based on approved inventory.

The short walkthrough is here: [recording link]. A verified review link is here: [verified preview link, if available]. All displayed suppliers, inventory and prices are synthetic. The accompanying requirements audit distinguishes implemented capability from remaining work, including the production WordPress integration.

I would welcome a discussion of the architecture and how I would adapt the prototype to your priorities and existing WordPress site.

Best regards,
[Your name]

Replace placeholders only with working links. Share the confidential case-study material or repository only with appropriate recipients and authorization; the recording can demonstrate the product without displaying the assessment PDF.
