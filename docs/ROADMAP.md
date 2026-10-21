# Delivery and production roadmap

The demonstration includes supplier → listing → approval → discovery → persisted inquiry, normalized associations, taxonomy/service-area/team controls, explainable concierge/preferences, supplier note assistance, factual insights and local photo-quality checks. The requirements audit separates this scope from production work.

## 1. Prepare the employer demonstration

1. Rehearse the 6–7 minute script in `EMPLOYER_PRESENTATION.md`. Explain the business objective and show the concierge before dashboards.
2. Prove one new offer is private before approval and public afterwards. Submit a fictional inquiry and show the same saved record in the supplier inbox.
3. Explain the shared eligibility rule, normalized data model, WordPress boundary and notification failure handling without reading code line by line.
4. Record locally while deployment is blocked. Label it a local prototype; do not send localhost as an external preview.
5. Share the recording, verified preview when available, and concise follow-up draft. Keep assessment documents private. Disclose AI-assisted development and distinguish the project from the written assessment.

## 2. Publish a review deployment

Complete Vercel/Neon account acceptance, provision the free database, apply migrations and seed fictional data with a unique review password. Deploy the API with durable database uploads, then the frontend with a server-side same-origin proxy. Verify critical workflows on the hosted URL before sharing. `DEPLOYMENT.md` records the runbook and blocker.

## 3. Stage WordPress integration

The bridge was activated and its catalog rendered in local WordPress/PHP. Test the company's staging theme/network/cache policy, introduce API-backed public vehicle routes and a WordPress inquiry form, preserve editorial/location URLs, and decide canonical URLs/redirects. Verify moderation invalidation, structured data, keyboard use and SEO before cutover.

## 4. Harden operations and measure scale

Use managed secrets, stronger session handling, shared rate limiting, monitoring and reviewed PII retention. Add a real notification worker/transport with backoff and concurrency controls. Move image bodies to object storage behind an adapter with lifecycle cleanup. Rehearse backup/restore, inspect PostgreSQL plans and run representative load/accessibility/security tests. Select caches/search infrastructure from measurements.

## 5. Evaluate richer AI deliberately

No-key paths work independently of paid services. Validate the optional provider with an authorized key and fixed evaluation set before calling it live-model verified. Extend grammar, negation, multilingual and unsupported-constraint clarifications with regression tests. Keep facts and authorization outside model authority. Evaluate semantic vehicle detection separately; local brightness/detail/hash checks do not verify vehicle identity/specifications. Predictive demand, learned personalization, dynamic pricing and fraud models require new evaluations.

Transactional reservations, payments, payouts and insurance remain outside Type A V1 and require separate product scope.
