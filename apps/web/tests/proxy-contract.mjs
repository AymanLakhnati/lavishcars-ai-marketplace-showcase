// Exercise the real server handler without opening a server or making network calls.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import ts from "typescript";
import { NextRequest } from "next/server.js";

const source = await readFile(new URL("../lib/server-proxy.ts", import.meta.url), "utf8");
const js = ts.transpileModule(source, {compilerOptions: {module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022}}).outputText;
const {proxyMarketplace} = await import("data:text/javascript;base64," + Buffer.from(js).toString("base64"));
const originalFetch = globalThis.fetch;
const originalOrigin = process.env.API_INTERNAL_ORIGIN;
const request = (path = "/api/v1/listings", init) => new NextRequest("http://localhost:3000" + path, init);
try {
  delete process.env.API_INTERNAL_ORIGIN;
  assert.equal((await proxyMarketplace(request(), ["listings"], "api/v1")).status, 503);
  process.env.API_INTERNAL_ORIGIN = "https://user:secret@example.com";
  assert.equal((await proxyMarketplace(request(), ["listings"], "api/v1")).status, 503);
  process.env.API_INTERNAL_ORIGIN = "https://api.example.com";
  assert.equal((await proxyMarketplace(request(), ["..", "private"], "api/v1")).status, 503);
  console.log("PASS: proxy rejects missing, credential-bearing and traversal configurations");

  globalThis.fetch = async (url, options) => {
    assert.equal(url.toString(), "https://api.example.com/api/v1/listings?city=Dubai");
    assert.equal(options.headers.get("authorization"), "Bearer synthetic-test-token");
    assert.equal(options.headers.get("cookie"), null);
    assert.equal(options.redirect, "manual");
    assert.equal(options.cache, "no-store");
    return Response.json({items: []});
  };
  const response = await proxyMarketplace(request("/api/v1/listings?city=Dubai", {headers: {Authorization: "Bearer synthetic-test-token", Cookie: "private=not-forwarded"}}), ["listings"], "api/v1");
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {items: []});
  console.log("PASS: proxy keeps fixed origin, forwards query/auth and excludes browser cookies");

  const large = request("/api/v1/supplier/uploads", {method: "POST", headers: {"Content-Length": String(10 * 1024 * 1024)}, body: "x"});
  assert.equal((await proxyMarketplace(large, ["supplier", "uploads"], "api/v1")).status, 413);
  console.log("PASS: oversized upload rejected before upstream request");

  globalThis.fetch = async () => new Response('{"detail":"Too many requests"}', {status: 429, headers: {"Content-Type": "application/json", "Retry-After": "60"}});
  const throttled = await proxyMarketplace(request(), ["listings"], "api/v1");
  assert.equal(throttled.status, 429);
  assert.equal(throttled.headers.get("retry-after"), "60");
  console.log("PASS: upstream throttling and retry policy survive proxy");

  globalThis.fetch = async () => {throw new Error("Synthetic unavailable upstream");};
  const unavailable = await proxyMarketplace(request(), ["listings"], "api/v1");
  assert.equal(unavailable.status, 503);
  assert((await unavailable.json()).detail.includes("temporarily unavailable"));
  console.log("PASS: upstream failure returns a structured service error");
} finally {
  globalThis.fetch = originalFetch;
  if (originalOrigin === undefined) delete process.env.API_INTERNAL_ORIGIN;
  else process.env.API_INTERNAL_ORIGIN = originalOrigin;
}
