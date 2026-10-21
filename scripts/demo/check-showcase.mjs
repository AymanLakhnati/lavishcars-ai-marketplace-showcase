import assert from "node:assert/strict";
import { chromium } from "@playwright/test";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
const source =
  process.env.SHOWCASE_URL ||
  pathToFileURL(resolve("review-site/dist/index.html")).href;
const browser = await chromium.launch({ headless: true });
const errors = [];
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(source, { waitUntil: "load" });
  await page
    .getByRole("heading", { name: "A marketplace. A working foundation." })
    .waitFor();
  assert.equal(await page.locator("[data-time]").count(), 9);
  await page.locator("#demo").evaluate((video) =>
    video.readyState >= 1
      ? null
      : new Promise((resolve, reject) => {
          video.addEventListener("loadedmetadata", resolve, { once: true });
          video.addEventListener("error", reject, { once: true });
        }),
  );
  const duration = await page
    .locator("#demo")
    .evaluate((video) => video.duration);
  assert(duration > 274 && duration < 277);
  await page.screenshot({
    path: "output/showcase/review-page-desktop.png",
    fullPage: true,
  });
  await page.locator('[data-time="205.347"]').click();
  await page.waitForFunction(
    () => document.querySelector("#demo").currentTime >= 205,
  );
  await page.locator("#demo").evaluate((video) => video.pause());
  assert(
    (await page
      .locator('[data-time="205.347"]')
      .getAttribute("aria-current")) === "true",
  );
  await page.getByRole("tab", { name: "02 / Supplier" }).click();
  assert.equal(
    await page.locator("#product-image").getAttribute("src"),
    "assets/supplier.png",
  );
  await page.getByRole("tab", { name: "02 / Supplier" }).press("ArrowRight");
  assert.equal(
    await page.locator("#tab-admin").getAttribute("aria-selected"),
    "true",
  );
  await page.getByRole("tab", { name: "03 / Administrator" }).press("End");
  assert.equal(
    await page.locator("#tab-concierge").getAttribute("aria-selected"),
    "true",
  );
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => scrollTo(0, 0));
  assert(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  );
  await page.screenshot({
    path: "output/showcase/review-page-mobile.png",
    fullPage: true,
  });
  assert.deepEqual(errors, []);
  console.log(
    "PASS: showcase desktop/mobile layout, nine chapter links, playable 4:35 video and chapter seeking; no browser runtime errors",
  );
} finally {
  await browser.close();
}
