"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { SlidersHorizontal, ArrowRight } from "lucide-react";
import { api, Listing } from "@/lib/api";
import { VehicleCard } from "@/components/vehicle";
function Fleet() {
  const params = useSearchParams();
  const router = useRouter();
  const [data, setData] = useState<{ items: Listing[]; total: number }>({
    items: [],
    total: 0,
  });
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [brands, setBrands] = useState<string[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [countries, setCountries] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  useEffect(() => {
    api<{ name: string }[]>("/models")
      .then((d) => setModels([...new Set(d.map((x) => x.name))]))
      .catch(() => {});
    api<{ name: string; kind: string; active: boolean }[]>("/locations")
      .then((d) => {
        setCities(
          d.filter((x) => x.kind === "city" && x.active).map((x) => x.name),
        );
        setCountries(
          d.filter((x) => x.kind === "country" && x.active).map((x) => x.name),
        );
      })
      .catch(() => {});
    api<{ name: string }[]>("/brands")
      .then((d) => setBrands(d.map((x) => x.name)))
      .catch(() => {});
    api<{ name: string }[]>("/categories")
      .then((d) => setCategories(d.map((x) => x.name)))
      .catch(() => {});
  }, []);
  const query = params.toString();
  useEffect(() => {
    const controller = new AbortController();
    setBusy(true);
    setError("");
    api<{ items: Listing[]; total: number }>(
      `/listings?page_size=12&${query}`,
      { signal: controller.signal },
    )
      .then(setData)
      .catch((e) => {
        if (!controller.signal.aborted) setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setBusy(false);
      });
    return () => controller.abort();
  }, [query]);
  function filter(key: string, value: string) {
    const p = new URLSearchParams(query);
    if (value) p.set(key, value);
    else p.delete(key);
    p.delete("page");
    router.push(`/fleet?${p}`);
  }
  const page = Number(params.get("page") || 1);
  const period = (
    ["daily", "weekly", "monthly"].includes(params.get("period") || "")
      ? params.get("period")
      : "daily"
  ) as "daily" | "weekly" | "monthly";
  return (
    <section className="section fleet-page">
      <div className="eyebrow">FIND YOUR NEXT CHAPTER</div>
      <div className="section-heading">
        <h1>
          The extraordinary,
          <br />
          <em>at your fingertips.</em>
        </h1>
        <p className="muted">
          A curated fleet. A world of possibility.
          <br />
          Every inquiry connects you to a rental partner.
        </p>
      </div>
      <div className="fleet-layout">
        <aside className="filter-panel">
          <h3>
            <SlidersHorizontal size={17} /> Refine your drive
          </h3>
          {[
            {
              key: "city",
              label: "Destination",
              options: cities,
            },
            { key: "country", label: "Country", options: countries },
            {
              key: "category",
              label: "Category",
              options: categories,
            },
            {
              key: "brand",
              label: "Brand",
              options: brands,
            },
            { key: "model", label: "Model", options: models },
            { key: "currency", label: "Currency", options: ["AED", "USD"] },
            {
              key: "vehicle_type",
              label: "Vehicle type",
              options: [
                "SUV",
                "Sedan",
                "Coupe",
                "Convertible",
                "Hatchback",
                "Van",
              ],
            },
            {
              key: "transmission",
              label: "Transmission",
              options: ["Automatic", "Manual"],
            },
          ].map((f) => (
            <label key={f.key}>
              {f.label}
              <select
                value={params.get(f.key) || ""}
                onChange={(e) => filter(f.key, e.target.value)}
              >
                <option value="">Any {f.label.toLowerCase()}</option>
                {f.options.map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </select>
            </label>
          ))}
          <label>
            Search brand or model
            <input
              value={params.get("q") || ""}
              onChange={(e) => filter("q", e.target.value)}
              placeholder="e.g. Porsche 911"
            />
          </label>
          <label>
            Rental rate period
            <select
              value={period}
              onChange={(e) => filter("period", e.target.value)}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </label>
          <label>
            Minimum {period} price
            <input
              type="number"
              min="0"
              value={params.get("min_price") || ""}
              onChange={(e) => filter("min_price", e.target.value)}
              placeholder="No minimum"
            />
          </label>
          <label>
            Maximum {period} price
            <input
              type="number"
              min="0"
              value={params.get("max_price") || ""}
              onChange={(e) => filter("max_price", e.target.value)}
              placeholder="No maximum"
            />
          </label>
          <label>
            Required features
            <input
              value={params.get("features") || ""}
              onChange={(e) => filter("features", e.target.value)}
              placeholder="Bluetooth, Sunroof"
            />
          </label>
          <label>
            Minimum seats
            <input
              type="number"
              min="1"
              max="20"
              value={params.get("seats") || ""}
              onChange={(e) => filter("seats", e.target.value)}
              placeholder="Any"
            />
          </label>
          <button className="text-link" onClick={() => router.push("/fleet")}>
            Reset filters
          </button>
          <p className="fineprint">
            Prices stay in their listed currency. Availability and final rates
            are confirmed by the supplier.
          </p>
        </aside>
        <div>
          <div className="results-toolbar">
            <span>
              {busy
                ? "Finding your next drive…"
                : `${data.total} vehicles to discover`}
            </span>
            <label className="sort-label">
              Sort by
              <select
                aria-label="Sort vehicles"
                value={params.get("sort") || "recommended"}
                onChange={(e) => filter("sort", e.target.value)}
              >
                <option value="recommended">Recommended</option>
                <option value="price_asc">Price: low to high</option>
                <option value="price_desc">Price: high to low</option>
                <option value="year_desc">Newest first</option>
              </select>
            </label>
          </div>
          {error ? (
            <div role="alert" className="error">
              {error}
            </div>
          ) : busy ? (
            <div className="vehicle-grid fleet-grid">
              {[1, 2, 3, 4].map((n) => (
                <div className="skeleton" key={n} />
              ))}
            </div>
          ) : data.items.length ? (
            <div className="vehicle-grid fleet-grid">
              {data.items.map((c) => (
                <VehicleCard listing={c} key={c.id} period={period} />
              ))}
            </div>
          ) : (
            <div className="empty">
              <h3>A different direction?</h3>
              <p>
                No approved cars match these filters. Try another destination or
                a wider budget.
              </p>
              <button
                className="button dark"
                onClick={() => router.push("/fleet")}
              >
                Explore all cars
              </button>
            </div>
          )}
          <div className="pagination">
            <button
              disabled={page === 1}
              onClick={() => {
                const p = new URLSearchParams(query);
                p.set("page", String(page - 1));
                router.push(`/fleet?${p}`);
              }}
            >
              Previous
            </button>
            <span>Page {page}</span>
            <button
              disabled={page * 12 >= data.total}
              onClick={() => {
                const p = new URLSearchParams(query);
                p.set("page", String(page + 1));
                router.push(`/fleet?${p}`);
              }}
            >
              Next <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
export default function FleetPage() {
  return (
    <Suspense fallback={<div className="section">Loading the collection…</div>}>
      <Fleet />
    </Suspense>
  );
}
