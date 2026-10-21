import { chromium } from "@playwright/test";
import assert from "node:assert/strict";

const base = process.env.WEB_URL || "http://localhost:3000";
const api = process.env.TEST_API_URL || "http://localhost:8000/api/v1";
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();
const failures = [];
page.on("pageerror", (error) => failures.push(error.message));
async function jsonResponse(path, action) {
  const responsePromise = page.waitForResponse(
    (r) => r.url().includes(path) && r.request().method() === "POST",
  );
  await action();
  const response = await responsePromise;
  assert(response.ok(), `${path}: ${await response.text()}`);
  return response.json();
}
try {
  await page.goto(`${base}/concierge`);
  await page
    .getByLabel("Describe your trip")
    .fill("A SUV for five passengers under AED 1000 per day");
  const initial = await jsonResponse("/ai/concierge", () =>
    page.getByRole("button", { name: "Find my drive" }).click(),
  );
  assert.equal(initial.needs_clarification, true);
  await page.getByLabel("Describe your trip").fill("Dubai");
  const clarified = await jsonResponse("/ai/concierge", () =>
    page.getByRole("button", { name: "Find my drive" }).click(),
  );
  assert.equal(clarified.filters.city, "Dubai");
  assert.equal(clarified.filters.seats, 5);
  assert.equal(clarified.filters.max_price, 1000);
  assert(clarified.recommendations.length > 0);
  console.log("PASS: clarification preserves budget and passenger constraints");

  await page.locator(".preference-section summary").click();
  await page.getByLabel("Maximum daily budget").fill("1000");
  const personalized = await jsonResponse("/ai/recommendations", () =>
    page.getByRole("button", { name: "Build my shortlist" }).click(),
  );
  assert(personalized.recommendations.length > 0);
  assert(
    personalized.recommendations.every((r) => r.listing.daily_price <= 1000),
  );
  console.log(
    "PASS: preference form returns eligible database recommendations",
  );

  await page.goto(`${base}/fleet?city=Dubai&period=weekly&features=Bluetooth`);
  await page.locator(".vehicle-card").first().waitFor();
  assert.equal(
    await page.getByLabel("Rental rate period").inputValue(),
    "weekly",
  );
  assert(
    (await page.locator(".card-bottom").first().innerText()).includes("/ week"),
  );
  console.log("PASS: weekly period and feature filters render catalog results");

  const supplierLogin = await fetch(`${api}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "supplier@lavish.demo",
      password: process.env.DEMO_PASSWORD || "DemoDrive!2026",
    }),
  });
  assert(supplierLogin.ok);
  await page.evaluate(
    (token) => localStorage.setItem("lavish_token", token),
    (await supplierLogin.json()).access_token,
  );
  await page.goto(`${base}/supplier`);
  await page.getByRole("button", { name: "Add vehicle" }).click();
  // Chromium does not expose multipart request sizes consistently. Observe the
  // actual File passed to fetch while leaving the request and response intact.
  await page.evaluate(() => {
    const originalFetch = window.fetch;
    window.fetch = function (input, init) {
      if (init?.body instanceof FormData) {
        const file = init.body.get("file");
        if (file instanceof File)
          window.__uploadedFile = { size: file.size, type: file.type };
      }
      return originalFetch.apply(this, arguments);
    };
  });
  const largePng = await page.evaluate(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 1500;
    canvas.height = 1000;
    const ctx = canvas.getContext("2d");
    const pixels = ctx.createImageData(canvas.width, canvas.height);
    let seed = 12345;
    for (let i = 0; i < pixels.data.length; i += 4) {
      for (let j = 0; j < 3; j++) {
        seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
        pixels.data[i + j] = seed >>> 24;
      }
      pixels.data[i + 3] = 255;
    }
    ctx.putImageData(pixels, 0, 0);
    return canvas.toDataURL("image/png").split(",")[1];
  });
  const original = Buffer.from(largePng, "base64");
  assert(
    original.length > 3 * 1024 * 1024 && original.length < 8 * 1024 * 1024,
  );
  const uploadPromise = page.waitForResponse(
    (r) =>
      r.url().includes("/supplier/uploads") && r.request().method() === "POST",
  );
  await page.locator('input[type="file"]').setInputFiles({
    name: "synthetic-noise.png",
    mimeType: "image/png",
    buffer: original,
  });
  const uploaded = await uploadPromise;
  assert(uploaded.ok(), await uploaded.text());
  const preparedFile = await page.evaluate(() => window.__uploadedFile);
  assert(preparedFile.size > 0 && preparedFile.size < 3 * 1024 * 1024);
  assert.equal(preparedFile.type, "image/webp");
  await page.locator(".upload-grid img").waitFor();
  console.log(
    "PASS: original 3–8 MB image is optimized to WebP and uploaded successfully",
  );

  const login = await fetch(`${api}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "admin@lavish.demo",
      password: process.env.DEMO_PASSWORD || "DemoDrive!2026",
    }),
  });
  assert(login.ok);
  const session = await login.json();
  await page.evaluate(
    (token) => localStorage.setItem("lavish_token", token),
    session.access_token,
  );
  await page.goto(`${base}/admin`);
  await page.getByRole("button", { name: "insights", exact: true }).click();
  await page.getByRole("heading", { name: "What the data tells us" }).waitFor();
  assert(
    (await page.locator(".insight-summary").innerText()).includes(
      "recorded inquiries",
    ),
  );
  console.log("PASS: admin insights display genuine scoped summaries");

  await page.getByRole("button", { name: "taxonomy", exact: true }).click();
  await page.getByRole("button", { name: "categories", exact: true }).click();
  await page.locator(".record").first().waitFor();
  await page
    .locator(".record")
    .first()
    .getByRole("button", { name: "Edit", exact: true })
    .click();
  await page.getByRole("button", { name: "Save reference" }).click();
  await page.getByText("Catalog reference saved.", { exact: true }).waitFor();
  console.log("PASS: taxonomy edit saves through admin API");

  await page.getByRole("button", { name: "listings", exact: true }).click();
  await page
    .getByRole("button", { name: "Edit listing", exact: true })
    .first()
    .click();
  await page.getByRole("button", { name: "Save listing changes" }).click();
  await page.getByText("Saved successfully.", { exact: true }).waitFor();
  console.log("PASS: administrative listing edit saves");
  assert.deepEqual(failures, [], "No browser runtime errors");
} finally {
  await browser.close();
}
