import { NextRequest } from "next/server";
import { proxyMarketplace } from "@/lib/server-proxy";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

async function handler(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  return proxyMarketplace(request, (await context.params).path, "api/v1");
}
export {
  handler as GET,
  handler as POST,
  handler as PUT,
  handler as PATCH,
  handler as DELETE,
};
