# Six-minute demonstration

Use the setup and seed commands in the root README. Start the API and storefront, verify `http://localhost:8000/health`, and use only synthetic names and contacts. The sequence below is a presentation script; it is not a test execution record. Read `IMPLEMENTATION_STATUS.md` before promising any optional feature.

## 0:00–0:45 — Establish the product

Open the homepage. Say: “This is an unofficial concept for a Type A listings marketplace. The inventory and prices are illustrative. Customers discover vehicles and request a quote; availability is confirmed separately by the supplier.”

Show the destination entry points and open `/fleet`. Select Dubai and SUV, then open a real listing. Point out currency, rental rate and specifications. Do not describe any offer as available for the user's dates.

## 0:45–1:45 — Showcase the concierge

Open `/concierge` and enter:

> I'm in Dubai for four days, looking for a luxury SUV under AED 1,000 per day.

Inspect the returned cards and match explanations. Compare a card to its public detail page. Explain: “These are eligible records from the database. The deterministic interpreter works without an API key. Up to three matching options are returned; there are no invented vehicles or prices.”

If the seed has fewer than three matching offers, present the actual result count. Change the budget to a value below every eligible offer to show the honest no-match state.

## 1:45–2:30 — Persist a customer inquiry

Open a matching vehicle at `/fleet/{slug}` and send a request using a fictitious name, an `example.com` email and a synthetic phone number. Select intended dates if supported. Show the confirmation. State that this is a saved request, not a reservation. Do not contact real suppliers or use production WhatsApp numbers.

## 2:30–3:45 — Supplier submission

Open `/supplier` and use the approved supplier demo account documented in the README. Show that supplier's listings and inquiries; identify the new inquiry if it belongs to that supplier. Use the listing assistant with “2026 Range Rover Sport SUV, automatic, five seats, Dubai, panoramic roof, AED 900 a day.” Preview its suggestions, explicitly apply them to the editable draft, and confirm the fields. Add a photo and a description of at least 20 characters, save and submit for review. Use its generated slug or ID to distinguish it from other offers. Show its pending status and verify that the public fleet does not show the new offer yet.

Use an approved supplier for this segment so supplier registration approval does not obscure the listing lifecycle. Explain that new supplier registration is separately subject to administrator approval.

## 3:45–5:00 — Administrative control

Open `/admin` in a separate browser session, or sign out before changing roles, and use the administrator demo account. Locate and approve the submitted offer. Return to the public fleet and show publication. Then demonstrate suspension using a supplier with published offers: the public catalog must exclude that supplier while its records remain in the admin interface. Restore the supplier through the supported approval workflow before repeating the demo.

Mention that supplier isolation and public-eligibility checks are enforced in the API. Cite only tests that actually passed in the root test report. Never imply a hidden button is the access-control boundary.

## 5:00–6:00 — WordPress and technical value

Show `docs/ARCHITECTURE.md` and the small plugin in `integrations/wordpress/`. Explain that WordPress keeps its existing marketing/editorial role while the API owns marketplace records. The included shortcode can render a filtered public catalog and link into the demonstration detail/inquiry flow. Say explicitly: “The WordPress adapter has been activated and its public catalog tested in local WordPress, including supplier suspension. Production WordPress detail pages and inquiry integration remain rollout work.”

Close with the working value: supplier-controlled offers, administrator approval, structured persistent inquiries and grounded recommendations. Refer to the status document for deferred scope such as live external-model verification and production operations.

## Reset and contingency

Reseed only using the documented local procedure and preserve any demonstration evidence you need first. Rehearse the exact database state before presenting. If the API is down, restore it; do not substitute static cards and imply a live result. If no suitable offers remain after moderation, restore eligible demo suppliers/listings and rerun the same query. External notification delivery is not required to prove an inquiry was saved; show the authorized CRM record and explain the outbox behavior accurately.
