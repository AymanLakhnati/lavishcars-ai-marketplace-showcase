import { chromium } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
const output = resolve("output/showcase");
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  await page.goto("http://127.0.0.1:8088/?page_id=4", {
    waitUntil: "networkidle",
  });
  await page
    .locator(".lavishcars-bridge")
    .screenshot({ path: resolve(output, "wordpress-catalog.png") });
  const text = await page.locator(".lavishcars-bridge").innerText();
  if (!text.includes("Cadillac") || !text.includes("G-Class"))
    throw new Error("Expected clean approved catalog in WordPress");
  await writeFile(
    resolve(output, "wordpress-verification.txt"),
    "Captured from real local WordPress at http://127.0.0.1:8088/?page_id=4\n" +
      text,
  );
  console.log("Captured real local WordPress catalog.");
} finally {
  await browser.close();
}
