import { NextRequest } from "next/server";

const MAX_BODY_BYTES = 9 * 1024 * 1024;

/** Fixed operator-owned origin; visitor input can only select an API path. */
export async function proxyMarketplace(
  request: NextRequest,
  segments: string[],
  resource: "api/v1" | "uploads",
) {
  const origin = process.env.API_INTERNAL_ORIGIN;
  if (!origin) {
    return Response.json(
      { detail: "The marketplace service is not configured." },
      { status: 503 },
    );
  }
  let target: URL;
  try {
    const configured = new URL(origin);
    if (
      !["http:", "https:"].includes(configured.protocol) ||
      configured.username ||
      configured.password
    )
      throw new Error();
    if (segments.some((s) => s === "." || s === ".." || s.includes("\\")))
      throw new Error();
    target = new URL(
      `/${resource}/${segments.map(encodeURIComponent).join("/")}`,
      configured.origin,
    );
    target.search = request.nextUrl.search;
  } catch {
    return Response.json(
      { detail: "Invalid marketplace route configuration." },
      { status: 503 },
    );
  }
  const headers = new Headers();
  for (const key of ["authorization", "content-type", "accept"]) {
    const value = request.headers.get(key);
    if (value) headers.set(key, value);
  }
  let body: Uint8Array | undefined;
  if (!["GET", "HEAD"].includes(request.method)) {
    if (Number(request.headers.get("content-length") || 0) > MAX_BODY_BYTES) {
      return Response.json(
        { detail: "The upload is too large." },
        { status: 413 },
      );
    }
    const reader = request.body?.getReader();
    const chunks: Uint8Array[] = [];
    let length = 0;
    if (reader) {
      for (;;) {
        const part = await reader.read();
        if (part.done) break;
        length += part.value.length;
        if (length > MAX_BODY_BYTES) {
          await reader.cancel();
          return Response.json(
            { detail: "The upload is too large." },
            { status: 413 },
          );
        }
        chunks.push(part.value);
      }
      body = new Uint8Array(length);
      let offset = 0;
      for (const chunk of chunks) {
        body.set(chunk, offset);
        offset += chunk.length;
      }
    }
  }
  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: body as BodyInit | undefined,
      redirect: "manual",
      cache: "no-store",
      signal: AbortSignal.timeout(resource === "uploads" ? 30_000 : 60_000),
    });
    const outputHeaders = new Headers({
      "Content-Type":
        upstream.headers.get("content-type") || "application/json",
      "X-Content-Type-Options": "nosniff",
      "Cache-Control":
        resource === "uploads" && upstream.ok
          ? "public, max-age=3600"
          : "no-store",
    });
    const retry = upstream.headers.get("retry-after");
    if (retry) outputHeaders.set("Retry-After", retry);
    return new Response(upstream.body, {
      status: upstream.status,
      headers: outputHeaders,
    });
  } catch {
    return Response.json(
      {
        detail:
          "The marketplace service is temporarily unavailable. Please try again.",
      },
      { status: 503 },
    );
  }
}
