"use client";
import { FormEvent, useState } from "react";
import { api, Listing } from "@/lib/api";
import { VehicleCard } from "@/components/vehicle";
type Result = {
  message: string;
  mode: string;
  recommendations: {
    listing: Listing;
    match_reasons: string[];
    score?: number;
  }[];
};
export function Preferences() {
  const [result, setResult] = useState<Result>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const f = new FormData(e.currentTarget);
    try {
      setResult(
        await api<Result>("/ai/recommendations", {
          method: "POST",
          body: JSON.stringify({
            city: f.get("city"),
            ...(f.get("max_price")
              ? { max_price: Number(f.get("max_price")) }
              : {}),
            ...(f.get("min_seats")
              ? { min_seats: Number(f.get("min_seats")) }
              : {}),
            occasion: f.get("occasion"),
            preferred_categories: f.getAll("preferred_categories"),
            features: f.getAll("features"),
          }),
        }),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="section preference-section" id="preferences">
      <details>
        <summary>
          <span className="eyebrow">A MORE PERSONAL SHORTLIST</span>
          <h2>Choose what matters to you.</h2>
          <p>
            Set your travel preferences for a ranked selection from the approved
            fleet.
          </p>
        </summary>
        <form onSubmit={submit} className="panel">
          <div className="editor-grid">
            <label>
              Destination
              <select name="city">
                <option>Dubai</option>
                <option>Houston</option>
                <option>Abu Dhabi</option>
                <option>Sharjah</option>
                <option>Miami</option>
              </select>
            </label>
            <label>
              Occasion
              <select name="occasion">
                <option value="leisure">A leisure trip</option>
                <option value="business">Business travel</option>
                <option value="family">Time with family</option>
                <option value="celebration">A celebration</option>
              </select>
            </label>
            <label>
              Maximum daily budget
              <input
                type="number"
                name="max_price"
                min={1}
                step="0.01"
                placeholder="Optional · destination currency"
              />
            </label>
            <label>
              Minimum seats
              <input
                type="number"
                name="min_seats"
                min={1}
                max={20}
                placeholder="Any"
              />
            </label>
          </div>
          <fieldset className="preference-options">
            <legend>Preferred categories</legend>
            {["SUV", "Sports", "Luxury", "Convertible", "Electric"].map((c) => (
              <label className="checkbox" key={c}>
                <input type="checkbox" name="preferred_categories" value={c} />
                {c}
              </label>
            ))}
          </fieldset>
          <fieldset className="preference-options">
            <legend>Features you value</legend>
            {[
              "Bluetooth",
              "Leather seats",
              "Sunroof",
              "Apple CarPlay",
              "Parking camera",
            ].map((f) => (
              <label className="checkbox" key={f}>
                <input type="checkbox" name="features" value={f} />
                {f}
              </label>
            ))}
          </fieldset>
          <p className="fineprint">
            Budget and passenger count are requirements. Preferred categories,
            occasion and features help rank suitable cars. Dubai and other UAE
            destinations use AED; US destinations use USD. No currency
            conversion.
          </p>
          <button className="button dark" disabled={busy}>
            {busy ? "Ranking your matches…" : "Build my shortlist"}
          </button>
        </form>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        {result && (
          <div aria-live="polite">
            <p className="description">{result.message}</p>
            <div className="vehicle-grid">
              {result.recommendations.map((r) => (
                <VehicleCard
                  key={r.listing.id}
                  listing={r.listing}
                  reasons={r.match_reasons}
                />
              ))}
            </div>
            <p className="fineprint">
              Recommendations use approved listing facts and your supplied
              preferences. Availability is confirmed by the supplier.
            </p>
          </div>
        )}
      </details>
    </section>
  );
}
