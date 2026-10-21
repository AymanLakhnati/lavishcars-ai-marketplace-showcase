"use client";
import { useEffect, useState } from "react";
import { BarChart3, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
type InsightsData = {
  listings_by_status: Record<string, number>;
  leads_by_status: Record<string, number>;
  totals: { listings: number; leads: number };
  leads_by_category: Record<string, number>;
  top_listings: {
    listing_id: number;
    title: string;
    inquiries: number;
    detail_requests: number;
    inquiries_per_100_detail_requests: number | null;
  }[];
  most_viewed?: {
    listing_id: number;
    title: string;
    detail_requests: number;
  }[];
  view_definition?: string;
  summaries: string[];
  scope: string;
  mode: string;
};
export function Insights() {
  const [data, setData] = useState<InsightsData>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function refresh() {
    setBusy(true);
    setError("");
    try {
      setData(await api<InsightsData>("/ai/marketplace-insights"));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    refresh();
  }, []);
  return (
    <div className="insights">
      <div className="section-heading">
        <div>
          <div className="eyebrow">
            <BarChart3 size={15} /> INTELLIGENCE FROM YOUR MARKETPLACE
          </div>
          <h2>A clearer view of what matters.</h2>
        </div>
        <button className="text-link" disabled={busy} onClick={refresh}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      {!data ? (
        busy && <p>Reading marketplace activity…</p>
      ) : (
        <>
          <p className="fineprint">
            Scope: {data.scope || "your authorized records"}. Live database
            aggregates. These are inquiry and listing counts, not revenue or
            confirmed bookings.
          </p>
          <div className="stats-row">
            <div>
              <small>Total listings</small>
              <strong>{data.totals.listings}</strong>
            </div>
            <div>
              <small>Customer inquiries</small>
              <strong>{data.totals.leads}</strong>
            </div>
            <div>
              <small>Awaiting review</small>
              <strong>{data.listings_by_status.pending || 0}</strong>
            </div>
            <div>
              <small>New inquiries</small>
              <strong>{data.leads_by_status.new || 0}</strong>
            </div>
          </div>
          <div className="insight-summary panel">
            <h3>What the data tells us</h3>
            {data.summaries.map((s, i) => (
              <p key={i}>{s}</p>
            ))}
          </div>
          <div className="insight-grid">
            {[
              ["Listing pipeline", data.listings_by_status],
              ["Inquiry pipeline", data.leads_by_status],
              ["Inquiry interest by category", data.leads_by_category],
            ].map(([title, values]) => (
              <div className="panel" key={String(title)}>
                <h3>{String(title)}</h3>
                {Object.entries(values as Record<string, number>).length ? (
                  Object.entries(values as Record<string, number>).map(
                    ([key, n]) => (
                      <div className="insight-bar" key={key}>
                        <div>
                          <span>{key.replaceAll("_", " ")}</span>
                          <strong>{n}</strong>
                        </div>
                        <meter
                          min={0}
                          max={Math.max(
                            1,
                            ...Object.values(values as Record<string, number>),
                          )}
                          value={n}
                        />
                      </div>
                    ),
                  )
                ) : (
                  <p className="muted">No activity recorded yet.</p>
                )}
              </div>
            ))}
          </div>
          <div className="panel">
            <h3>Most inquired-about vehicles</h3>
            {data.top_listings.length ? (
              data.top_listings.map((l) => (
                <div className="insight-top" key={l.listing_id}>
                  <span>{l.title}</span>
                  <strong>
                    {l.inquiries} {l.inquiries === 1 ? "inquiry" : "inquiries"}
                    {l.detail_requests > 0 && (
                      <small>
                        {" "}
                        · {l.detail_requests} detail requests ·{" "}
                        {l.inquiries_per_100_detail_requests} inquiries / 100
                        requests
                      </small>
                    )}
                  </strong>
                </div>
              ))
            ) : (
              <p className="muted">
                Vehicle interest will appear when customer inquiries are saved.
              </p>
            )}
          </div>
          <div className="panel">
            <h3>Most viewed vehicle details</h3>
            <p className="fineprint">{data.view_definition}</p>
            {data.most_viewed?.length ? (
              data.most_viewed.map((item) => (
                <div className="insight-top" key={item.listing_id}>
                  <span>{item.title}</span>
                  <strong>{item.detail_requests} requests</strong>
                </div>
              ))
            ) : (
              <p className="muted">
                Open a public vehicle detail page to begin recording activity.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
