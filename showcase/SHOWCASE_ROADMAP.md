# Employer presentation roadmap

Prepared for Ayman Lakhnati. Use the links below directly; no confidential assessment attachment is included.

- Review website and video: https://lavishcars-ayman-showcase.jocund-larch-4775.chatgpt.site
- Public repository: https://github.com/AymanLakhnati/lavishcars-ai-marketplace-showcase
- Direct video: https://lavishcars-ayman-showcase.jocund-larch-4775.chatgpt.site/assets/LavishCars-Demo.mp4
- Source ZIP: https://lavishcars-ayman-showcase.jocund-larch-4775.chatgpt.site/assets/LavishCars-Source.zip

## Before submitting

Send the prepared email with the review website and repository links. The employer does not need an account to read the public code. No large attachment is required. Recheck both links in a signed-out browser before sending. Do not call the full marketplace publicly deployed: the published site is a review presentation with recorded captures, video and resources.

## A persuasive 10-minute conversation

1. **0:00–0:45 — Business problem.** “I focused first on the Type A workflow: supplier → offer → approval → discovery → saved inquiry. AI supports that workflow.”
2. **0:45–3:00 — Product.** Show the marketplace, supplier and admin chapters. Explain filtering, supplier ownership, moderation reasons, lifecycle actions and server-enforced visibility. The published gallery contains recorded states; local controls require the application setup.
3. **3:00–5:00 — Showcase moment.** Play the concierge chapter at 02:13. Use the Dubai SUV example: under AED 1,000/day, four days. Point to three stored offers and their actual daily prices. Explain that the prototype does not confirm availability or reservations and does not compute a final contract price.
4. **5:00–6:30 — Other assistance.** Preview editable supplier suggestions and explain preference weights, factual insights and basic photo checks. State that no-key interpretation is deterministic; do not describe it as a verified live language model.
5. **6:30–8:30 — Code.** Open `services/api/app/catalog.py` for public eligibility, `main.py` for ownership/moderation/inquiries, and the AI service modules. Show backend tests for a failure boundary. The inquiry/outbox atomic commit is a useful engineering example.
6. **8:30–10:00 — Fit and next steps.** Discuss WordPress integration, production operations and which business assumption the team would validate first. Ask which workflow they consider highest priority.

## Video chapters

00:00 Marketplace introduction
00:21 Discovery and inquiry
00:50 Supplier dashboard
01:16 Administrator dashboard
01:44 Approval-to-inquiry and WordPress
02:13 AI concierge
02:49 Preferences and supplier assistant
03:25 Insights and photo assistance
03:54 Engineering and closing

## Questions to prepare for

**Why separate FastAPI from WordPress?** The API owns marketplace permissions and lifecycle rules; WordPress remains the intended content/marketing/SEO layer. The tested bridge is a local catalog integration, not a completed production WordPress rollout.

**How do you prevent invented offers?** Results use eligible database records. Shared server-side rules check publication, supplier state and location eligibility. Model-suggested fields are validated and reviewed.

**Which AI really works?** Deterministic concierge parsing, rule-based preferences, editable note extraction, database summaries and image-quality heuristics were verified locally. The optional external provider is mock-tested; a real provider call is unverified. Semantic vehicle recognition is absent.

**What was tested?** 22 backend tests, 4 main browser scenarios, 7 extended interface checks, 5 proxy checks, migrations and local WordPress integration. The latest storefront changes passed production build and lint. Remote CI failed before test steps; do not present it as green.

**What would you ship next?** Stage the complete application with PostgreSQL and production secrets; verify model integration, real notification delivery, abuse controls, backups and WordPress routes. Then validate the end-to-end flow with business users before adding ambitious AI.

**How was AI involved?** Be direct: AI assisted implementation and preparation. Explain the code, the trade-offs and the tests yourself; do not imply entirely unaided authorship.

## Production roadmap with acceptance gates

1. **Staging foundation:** provision API/web/PostgreSQL, run migrations, remove public demo credentials, configure TLS/secrets/storage. Gate: authenticated supplier-to-inquiry smoke test succeeds on the staged system.
2. **Operational reliability:** real notification worker with retry/monitoring, shared rate limits, backups with restore exercise, privacy/session review. Gate: delivery failure preserves the inquiry and recovery is demonstrated.
3. **Verified model integration:** configure an authorized provider, run grounded-result and failure/timeout evaluations, measure cost/latency. Gate: constraints, prices and eligibility remain correct on the agreed evaluation set.
4. **WordPress rollout:** agree theme/detail routes/canonicals, caching invalidation and inquiry embedding. Gate: supplier suspension removes public results across both surfaces and SEO routes behave correctly.
5. **Pilot:** supplier acceptance tests, accessibility and performance checks, support ownership and monitoring. Gate: the business accepts the pilot against a written checklist.

This is a reviewable prototype, not a production or recruitment guarantee.
