# WordPress routing bridge

This is a thin concept plugin. PHP lint, activation and shortcode rendering were verified in a real local WordPress installation with PHP 8.4.26. The integration check also verified suspension/removal and restoration on the next render. It is not deployed to the company site and has not been tested with its production theme. It retrieves public catalog records on the server and links to the Next.js demonstration vehicle and inquiry flow. It does not register supplier accounts, copy listings into posts, accept credentials, or store inquiries in WordPress.

## Local installation

1. Run the marketplace API and Next.js storefront using the root README.
2. Copy the `lavishcars-marketplace` directory into a local WordPress installation's `wp-content/plugins/` and activate **LavishCars Marketplace Bridge (Concept)**.
3. Set these constants in that installation's `wp-config.php` before the final bootstrap:

```php
define('LAVISHCARS_API_ORIGIN', 'http://127.0.0.1:8000');
define('LAVISHCARS_STOREFRONT_ORIGIN', 'http://localhost:3000');
```

The API origin must be reachable **from the WordPress server**. If WordPress runs in Docker, `127.0.0.1` refers to its own container: use an operator-configured reachable API service name instead. The storefront origin must be reachable **from the visitor's browser**. Use HTTPS origins for a hosted integration.

4. Add `[lavishcars_catalog city="Dubai" category="SUV" limit="6"]` to a page. Omit filters for the first catalog page. Limit is bounded to 1–12. This is an editorial component, not an interactive full fleet browser.
5. Check catalog rendering, no-results behavior, API downtime, link navigation, quote submission, and visibility after supplier suspension in that WordPress environment.

## Ownership and security

The FastAPI public endpoint determines visibility; WordPress receives only public listing data. The adapter only calls the explicitly configured origin and a fixed API path. It disables redirects, limits response size and timeout, bounds shortcode parameters, and escapes all rendered strings and URLs. It does not accept a remote URL from visitor input. No credentials or private records are sent to WordPress. There is no response cache in the plugin. Disable page/CDN caching on these demo catalog pages if immediate suspension visibility is required; otherwise cached HTML can be stale even though the API is correct.

## Production routing and SEO work still needed

Existing WordPress content, editorial pages, locations, brands and categories can remain at their current URLs. This demo bridge navigates to `/fleet/{slug}` in Next.js to show details and collect an inquiry. It is **not** a production replacement for WordPress public vehicle pages.

Before production, implement and test server-rendered WordPress detail routes backed by `GET /api/v1/listings/{slug}`, preserving or redirecting existing permalinks and selecting a single canonical detail URL. Add structured data only from authoritative records without availability claims. Make unavailable/hidden listings return an appropriate not-found response. Integrate a WordPress inquiry form with `POST /api/v1/leads` using server-side validation, anti-abuse controls, and the same persistence-before-notification semantics. Until then, this plugin deliberately routes inquiries to the functioning storefront form. Test theme compatibility, keyboard use, deployment network policy, caching invalidation, and SEO on a staging WordPress instance before rollout.
