import { test, expect } from "@playwright/test";

const API = process.env.TEST_API_URL || "http://localhost:8000/api/v1";
const password = process.env.DEMO_PASSWORD || "DemoDrive!2026";

test("concierge returns three real matching cars and an inquiry reaches the supplier", async ({ page, request }) => {
  await page.goto("/concierge");
  await page.getByLabel("Describe your trip").fill(
    "I'm in Dubai for four days, looking for a luxury SUV under AED 1,000 per day.",
  );
  const responsePromise = page.waitForResponse(r => r.url().endsWith("/ai/concierge") && r.request().method() === "POST");
  await page.getByRole("button", { name: "Find my drive" }).click();
  const response = await responsePromise;
  expect(response.ok()).toBeTruthy();
  const answer = await response.json();
  expect(answer.recommendations).toHaveLength(3);
  for (const rec of answer.recommendations) {
    expect(rec.listing.city).toBe("Dubai");
    expect(rec.listing.currency).toBe("AED");
    expect(Number(rec.listing.daily_price)).toBeLessThan(1000);
    expect(rec.listing.category).toBe("SUV");
    expect(rec.match_reasons.length).toBeGreaterThan(0);
    const real = await request.get(`${API}/listings/${rec.listing.slug}`);
    expect(real.ok()).toBeTruthy();
    expect((await real.json()).id).toBe(rec.listing.id);
  }
  await expect(page.getByRole("heading", { name: "Your next drive, shortlisted." })).toBeVisible();
  await page.screenshot({ path: "test-results/concierge-desktop.png", fullPage: true });
  await page.locator(`a[href="/fleet/${answer.recommendations[0].listing.slug}"]`).first().click();
  await page.getByLabel("Full name").fill("Demo Browser Guest");
  const email = `browser-${Date.now()}@example.com`;
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Phone number").fill("+15550102030");
  await page.getByLabel("Your plans").fill("Synthetic test inquiry for a four day Dubai trip.");
  await page.getByRole("checkbox").check();
  const inquiryPromise = page.waitForResponse(r => r.url().endsWith("/leads") && r.request().method() === "POST");
  await page.getByRole("button", { name: "Request a quote" }).click();
  const inquiry = await inquiryPromise;
  expect(inquiry.ok()).toBeTruthy();
  const lead = await inquiry.json();
  await expect(page.getByRole("heading", { name: "Your inquiry is in." })).toBeVisible();
  const login = await request.post(`${API}/auth/login`, { data: { email: "admin@lavish.demo", password } });
  expect(login.ok()).toBeTruthy();
  const { access_token } = await login.json();
  const leads = await request.get(`${API}/admin/leads`, { headers: { Authorization: `Bearer ${access_token}` } });
  expect((await leads.json()).items.some((item: { id: number; email: string }) => item.id === lead.id && item.email === email)).toBeTruthy();
});

test("catalog filters are URL based and mobile layout fits the viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/fleet?city=Dubai&category=SUV&max_price=1000");
  await expect(page.getByText(/vehicles to discover/)).toBeVisible();
  await expect(page.getByRole("combobox", { name: "Destination", exact: true })).toHaveValue("Dubai");
  await expect(page.getByRole("combobox", { name: "Category", exact: true })).toHaveValue("SUV");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.screenshot({ path: "test-results/fleet-mobile.png", fullPage: true });
});

test("homepage renders the live catalog", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Don’t just arrive/ })).toBeVisible();
  await expect(page.locator('a[href^="/fleet/"]').first()).toBeVisible();
  await page.screenshot({ path: "test-results/home-desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole("button", { name: "Toggle navigation" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.screenshot({ path: "test-results/home-mobile.png", fullPage: true });
});

test("supplier submits a photographed listing, admin approves it, and a customer inquires", async ({ page, request }) => {
  const supplierLogin = await request.post(`${API}/auth/login`, {
    data: { email: "supplier@lavish.demo", password },
  });
  expect(supplierLogin.ok()).toBeTruthy();
  const supplierToken = (await supplierLogin.json()).access_token;
  await page.goto("/supplier");
  await page.evaluate((token) => localStorage.setItem("lavish_token", token), supplierToken);
  await page.reload();
  await expect(page.getByRole("heading", { name: /Desert Atelier Motors/ })).toBeVisible();
  await page.getByRole("button", { name: "Add vehicle" }).click();

  await page.getByLabel("Vehicle notes").fill(
    "2026 Range Rover Sport SUV, automatic, five seats, Dubai, panoramic roof, AED 777 a day.",
  );
  await page.getByRole("button", { name: "Preview suggestions" }).click();
  await expect(page.getByRole("heading", { name: "Review your suggested details" })).toBeVisible();
  await page.getByRole("button", { name: "Apply suggestions to draft" }).click();
  await page.getByLabel("Category").fill("SUV");
  await page.getByLabel("Description").fill(
    "Synthetic browser-test Range Rover listing with a supplier-confirmed illustrative rate.",
  );
  await page.getByLabel("Vehicle photography").setInputFiles({
    name: "vehicle.png",
    mimeType: "image/png",
    buffer: Buffer.from(
      "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAAAC64paAAAALElEQVR4nGOUMFBnIBcwka2TYVQzyYCJdC0IMKqZRMBEqgZkMKqZREBRgAEAdEEAl6i18u8AAAAASUVORK5CYII=",
      "base64",
    ),
  });
  await expect(page.getByAltText("Vehicle upload 1")).toBeVisible();
  const savePromise = page.waitForResponse(r => r.url().endsWith("/supplier/listings") && r.request().method() === "POST");
  await page.getByRole("button", { name: "Save draft" }).click();
  const saved = await savePromise;
  expect(saved.ok()).toBeTruthy();
  const created = await saved.json();
  const supplierRecord = page.locator(".record").filter({ hasText: "AED 777" }).first();
  await expect(supplierRecord).toContainText("draft");
  await supplierRecord.getByRole("button", { name: "Submit for review" }).click();
  await expect(supplierRecord).toContainText("pending");
  expect((await request.get(`${API}/listings/${created.slug}`)).status()).toBe(404);
  await page.screenshot({ path: "test-results/supplier-desktop.png", fullPage: true });

  const adminLogin = await request.post(`${API}/auth/login`, {
    data: { email: "admin@lavish.demo", password },
  });
  const adminToken = (await adminLogin.json()).access_token;
  await page.evaluate((token) => localStorage.setItem("lavish_token", token), adminToken);
  await page.goto("/admin");
  const adminRecord = page.locator(".record").filter({ hasText: "AED 777" }).first();
  await expect(adminRecord).toContainText("pending");
  await adminRecord.getByRole("button", { name: "Approve" }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Confirm" }).click();
  await expect(adminRecord).toContainText("published");
  await page.screenshot({ path: "test-results/admin-desktop.png", fullPage: true });

  const publicResult = await request.get(`${API}/listings?city=Dubai&max_price=777`);
  const approved = (await publicResult.json()).items.find(
    (item: { id: number }) => item.id === created.id,
  );
  expect(approved).toBeTruthy();
  await page.evaluate(() => localStorage.removeItem("lavish_token"));
  await page.goto(`/fleet/${approved.slug}`);
  await page.getByLabel("Full name").fill("Vertical Slice Visitor");
  await page.getByLabel("Email address").fill(`vertical-${Date.now()}@example.com`);
  await page.getByLabel("Phone number").fill("+15550109999");
  await page.getByLabel("Your plans").fill("Synthetic inquiry for the newly approved listing.");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Request a quote" }).click();
  await expect(page.getByRole("heading", { name: "Your inquiry is in." })).toBeVisible();
  const cleanup = await request.post(`${API}/supplier/listings/${approved.id}/archive`, {
    headers: { Authorization: `Bearer ${supplierToken}` },
  });
  expect(cleanup.ok()).toBeTruthy();
});
