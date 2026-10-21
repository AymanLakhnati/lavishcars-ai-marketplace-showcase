"use client";
import { useState, FormEvent } from "react";
import { Sparkles, ArrowUpRight, ArrowRight, Check } from "lucide-react";
import { api, Listing } from "@/lib/api";
import { VehicleCard } from "@/components/vehicle";
import { Preferences } from "@/components/preferences";
type Answer = {
  message: string;
  mode: string;
  filters: Record<string, unknown>;
  recommendations: { listing: Listing; match_reasons: string[] }[];
  needs_clarification?: boolean;
};
const prompts = [
  "A stylish SUV in Dubai for under AED 1,000 a day",
  "A convertible in Houston for a weekend trip",
  "A spacious luxury car in Dubai for five passengers",
];
export default function Concierge() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState<Answer>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [context, setContext] = useState("");
  async function ask(text: string, fresh = false) {
    if (!text.trim()) return;
    setMessage(text);
    setBusy(true);
    setError("");
    try {
      const safeText = text
        .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, "[contact removed]")
        .replace(/\+\d[\d\s()-]{8,}\d/g, "[contact removed]");
      const combined =
        !fresh && context
          ? `${context}\nAdditional trip detail: ${safeText}`
          : safeText;
      if (combined.length > 2000)
        throw new Error(
          "Your trip details are getting long. Start a new search to describe your updated preferences.",
        );
      const result = await api<Answer>("/ai/concierge", {
        method: "POST",
        body: JSON.stringify({ message: combined }),
      });
      setAnswer(result);
      const clarification =
        result.needs_clarification ??
        (!result.recommendations.length &&
          /\?|please (provide|give)/i.test(result.message));
      setContext(clarification ? combined : "");
      if (clarification) setMessage("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function submit(e: FormEvent) {
    e.preventDefault();
    ask(message);
  }
  return (
    <>
      <section className="concierge-intro">
        <div className="ai-orbit">
          <Sparkles size={30} />
        </div>
        <div className="eyebrow">THE LAVISH CONCIERGE</div>
        <h1>
          A great drive begins
          <br />
          with <em>a conversation.</em>
        </h1>
        <p>
          A weekend away. A special arrival. A little more room.
          <br />
          Tell us what you have in mind. We’ll find your fit.
        </p>
        <form className="concierge-form" onSubmit={submit}>
          <label className="sr-only" htmlFor="trip">
            Describe your trip
          </label>
          <textarea
            id="trip"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            maxLength={2000}
            placeholder="I’m visiting Dubai for five days. I’d love a stylish SUV under AED 1,000 a day…"
            rows={3}
            required
          />
          <div>
            <span>
              <Sparkles size={14} /> Grounded in our approved fleet
            </span>
            <button className="button dark" disabled={busy}>
              {busy ? "Finding your fit…" : "Find my drive"}
              <ArrowUpRight size={17} />
            </button>
          </div>
        </form>
        {context && (
          <div className="clarification-context">
            <p>
              <strong>Your trip so far:</strong> {context}
            </p>
            <button
              className="text-link"
              onClick={() => {
                setContext("");
                setAnswer(undefined);
                setMessage("");
              }}
            >
              Start a new search
            </button>
            <p className="fineprint">
              Add the missing detail above. Your earlier preferences will be
              kept for this search. Please leave out personal contact details.
            </p>
          </div>
        )}
        <div className="prompt-chips">
          {prompts.map((p) => (
            <button key={p} disabled={busy} onClick={() => ask(p, true)}>
              {p}
              <ArrowRight size={13} />
            </button>
          ))}
        </div>
        <div className="concierge-assurance">
          <span>
            <Check size={14} /> Real catalog matches
          </span>
          <span>
            <Check size={14} /> Transparent prices
          </span>
          <span>
            <Check size={14} /> No booking commitments
          </span>
        </div>
      </section>
      <Preferences />
      {error && (
        <div className="section">
          <div className="error" role="alert">
            {error}
          </div>
        </div>
      )}
      {answer && (
        <section className="section concierge-results" aria-live="polite">
          <div className="section-heading">
            <div>
              <div className="eyebrow">CONSIDERED FOR YOU</div>
              <h2>
                {answer.recommendations.length
                  ? "Your next drive, shortlisted."
                  : "Let’s refine your search."}
              </h2>
              <p>{answer.message}</p>
            </div>
            <span className="status">
              {answer.mode === "deterministic"
                ? "Smart matching · demo mode"
                : "AI assisted matching"}
            </span>
          </div>
          <div className="filter-chips">
            {Object.entries(answer.filters)
              .filter(([, v]) => v !== null && v !== "" && v !== undefined)
              .map(([k, v]) => (
                <span key={k}>
                  {k.replaceAll("_", " ")}:{" "}
                  {Array.isArray(v) ? v.join(", ") : String(v)}
                </span>
              ))}
          </div>
          <div className="vehicle-grid">
            {answer.recommendations.map((r) => (
              <VehicleCard
                listing={r.listing}
                reasons={r.match_reasons}
                key={r.listing.id}
              />
            ))}
          </div>
          <p className="fineprint">
            Recommendations reflect approved catalog information, not real-time
            availability. Rates are in each vehicle’s listed currency.{" "}
            {answer.mode === "deterministic"
              ? "This demo uses transparent rules to interpret your request; no language model is connected."
              : ""}
          </p>
        </section>
      )}
    </>
  );
}
