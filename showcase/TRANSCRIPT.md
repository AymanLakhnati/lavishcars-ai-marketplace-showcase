# Narrated demonstration transcript

Synthetic English narration; verified captures and fresh local API evidence.

## 00:00:00.000 — A marketplace built around trust

After the LavishCars technical assessment, Ayman Lakhnati developed this independent, AI-assisted marketplace concept. The objective is practical: help suppliers publish approved offers, help customers discover suitable vehicles, and turn interest into structured inquiries. This walkthrough combines verified prototype screens with fresh API demonstrations. All suppliers, vehicles and prices are synthetic. It is a listings marketplace, with no payment or confirmed reservation.

## 00:00:34.508 — Describe the trip. Discover the drive.

The showcase begins with a simple request: a luxury S U V in Dubai, for four days, below one thousand dirhams per day. The concierge extracts supported constraints, queries approved inventory, and returns up to three real database records with prices and explanations. It can ask for a missing destination while preserving earlier budget and passenger details. The database remains authoritative for price, supplier eligibility and visibility. The no-key interpretation is deterministic, so the demonstration works without a paid model. An optional external-provider adapter is implemented, but a real model call has not been verified.

## 00:01:18.510 — A shortlist with reasons, not guesses

The preference service makes the ranking explicit. Destination, budget, passenger capacity and required features constrain the eligible offers. A preferred category adds twenty ranking points, and an editorial occasion match adds ten. Ties use daily price, then listing identity. These are transparent rules, not invented match percentages or machine-learning accuracy claims. The customer can inspect the same vehicle record and request a quote. An inquiry is saved with its responsible listing, supplier and location before any notification attempt. It remains an inquiry, never a booking guarantee.

## 00:02:01.436 — From rough notes to a reviewable offer

For suppliers, the listing assistant turns rough vehicle notes into suggested fields, a concise description and completeness warnings. It recognizes existing catalog references and explicitly supplied facts. Unknown specifications remain for review. Suggestions must be previewed and applied to an editable draft. Applying them does not save, submit or publish a vehicle. The supplier still checks the details, uploads permitted images, saves the offer and submits it for administrator review. Supplier identity comes from authentication, and private listings and inquiries are scoped to that supplier.

## 00:02:43.368 — Publication is a business rule

Administrator approval is a real boundary in the backend. A published offer also requires an approved, active supplier, an enabled market and no administrative hide. The same eligibility rule protects public search, vehicle details, recommendations and new inquiries. Supplier suspension removes public visibility without deleting business records. Material listing edits require renewed review. Customer inquiries are stored as structured C R M records, with controlled status updates. A notification failure cannot erase the saved request because the inquiry and outbox event commit together.

## 00:03:24.649 — Useful intelligence, backed by evidence

The insights service summarizes actual account data: listing states, inquiry states, category interest and the most-viewed vehicle details. View metrics count detail A P I requests, including repeats and automated demonstrations. They are descriptive measures, not unique-customer conversion or demand forecasts. Photo assistance checks resolution, brightness and edge detail, detects identical normalized uploads, and provides a documented cover-candidate score. These local image heuristics support supplier review. They do not verify that a photograph contains a vehicle, establish ownership, or infer exact specifications.

## 00:04:08.860 — Respect WordPress. Separate the authority.

The architecture respects LavishCars' existing WordPress investment. WordPress remains the intended marketing, content and S E O layer. Fast A P I and PostgreSQL own suppliers, normalized memberships, service areas, offers, approvals and inquiries. Next J S demonstrates the storefront and portals. A local WordPress bridge has been tested for catalog rendering and supplier suspension visibility. Verification includes twenty-two backend tests, four main browser scenarios, seven extended interface checks and five proxy checks. The build and lint pass locally. Remote continuous integration has a startup failure, and public deployment is still blocked by the hosting account setup.

## 00:04:58.950 — Business understanding. Working evidence.

The result is a reviewable demonstration of the complete supplier-to-inquiry workflow, with grounded assistance where it helps. The repository includes the architecture, requirement audit, tests and an explicit production roadmap. The next conversation is about scope, trade-offs and how this foundation should fit LavishCars' priorities. This is an unofficial concept developed with AI assistance. The voice narration is synthetic.
