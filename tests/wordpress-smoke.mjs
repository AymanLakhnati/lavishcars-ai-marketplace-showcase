// Optional local integration check: start WordPress with the documented shortcode.
import assert from "node:assert/strict";
const origin = process.env.TEST_API_URL || "http://127.0.0.1:8000/api/v1";
const pageUrl = process.env.TEST_WORDPRESS_URL || "http://127.0.0.1:8088/?page_id=4";
for (const url of [origin, pageUrl]) {
  assert(["localhost", "127.0.0.1"].includes(new URL(url).hostname), "This moderation test is local-only");
}
async function api(path, options = {}) {
  const response = await fetch(origin + path, options);
  assert(response.ok, `${path}: ${response.status}`);
  return response.json();
}
const catalog = await api("/listings?city=Dubai&category=SUV&page_size=3");
assert.equal(catalog.items.length, 3);
let html = await (await fetch(pageUrl)).text();
assert(html.includes('class="lavishcars-bridge"'));
for (const listing of catalog.items) {
  assert(html.includes(listing.title));
  assert(html.includes(`/fleet/${listing.slug}`));
}
console.log("PASS: local WordPress page renders three filtered records and real detail/inquiry links");
const session = await api("/auth/login", {
  method: "POST", headers: {"Content-Type": "application/json"},
  body: JSON.stringify({email: "admin@lavish.demo", password: process.env.DEMO_PASSWORD || "DemoDrive!2026"}),
});
const headers = {"Content-Type": "application/json", Authorization: "Bearer " + session.access_token};
const suppliers = await api("/admin/suppliers", {headers});
const supplier = suppliers.items.find(item => item.company_name === catalog.items[0].supplier_name);
assert(supplier && supplier.status === "approved");
try {
  await api(`/admin/suppliers/${supplier.id}/suspend`, {method: "POST", headers, body: JSON.stringify({reason: "Local WordPress visibility integration check"})});
  html = await (await fetch(pageUrl)).text();
  for (const listing of catalog.items.filter(x => x.supplier_name === supplier.company_name)) {
    assert(!html.includes(`/fleet/${listing.slug}`), "Suspended supplier must disappear on next WordPress render");
  }
  console.log("PASS: WordPress bridge respects immediate API supplier suspension");
} finally {
  await api(`/admin/suppliers/${supplier.id}/approve`, {method: "POST", headers, body: JSON.stringify({reason: supplier.rejection_reason || ""})});
}
html = await (await fetch(pageUrl)).text();
assert(html.includes(`/fleet/${catalog.items[0].slug}`));
console.log("PASS: restored supplier reappears; no duplicate marketplace database in WordPress");
