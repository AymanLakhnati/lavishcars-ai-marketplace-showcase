export const API =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export type Listing = {
  id: number;
  slug: string;
  brand: string;
  model: string;
  year: number;
  trim?: string;
  vehicle_type?: string;
  categories?: string[];
  city: string;
  country: string;
  category: string;
  currency: string;
  daily_price: number;
  weekly_price?: number;
  monthly_price?: number;
  seats: number;
  transmission: string;
  description: string;
  features: string[];
  images: string[];
  supplier_name: string;
  status: string;
  rejection_reason?: string;
  deposit?: number;
  mileage?: string;
};
export type User = {
  id: number;
  email: string;
  role: string;
  supplier_id?: number;
};
export function token() {
  return typeof window !== "undefined"
    ? localStorage.getItem("lavish_token")
    : null;
}
export async function api<T = Record<string, unknown>>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const t = token();
  const headers: Record<string, string> = {
    ...(options.body instanceof FormData
      ? {}
      : { "Content-Type": "application/json" }),
    ...(t ? { Authorization: `Bearer ${t}` } : {}),
  };
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({
      detail: "The service could not complete this request.",
    }));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : Array.isArray(body.detail)
          ? body.detail
              .map(
                (item: { msg?: string; loc?: string[] }) =>
                  `${item.loc?.slice(1).join(" ") || "Request"}: ${item.msg || "Invalid value"}`,
              )
              .join(". ")
          : "The request could not be completed.",
    );
  }
  return res.status === 204 ? ({} as T) : res.json();
}
export function mediaUrl(url: string) {
  return url.startsWith("/") ? API.replace(/\/api\/v1\/?$/, "") + url : url;
}
export function price(value: number | undefined, currency: string) {
  return value == null
    ? "On request"
    : `${currency} ${Number(value).toLocaleString("en-US", { maximumFractionDigits: 2 })}`;
}
