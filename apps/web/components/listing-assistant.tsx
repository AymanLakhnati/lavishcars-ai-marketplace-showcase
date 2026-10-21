"use client";
import { useState } from "react";
import { Sparkles, Check } from "lucide-react";
import { api } from "@/lib/api";
type Draft = {
  suggestions: Record<string, unknown>;
  missing_fields: string[];
  warnings: string[];
  mode: string;
};
export function ListingAssistant({
  onApply,
}: {
  onApply: (suggestions: Record<string, unknown>) => void;
}) {
  const [notes, setNotes] = useState("");
  const [result, setResult] = useState<Draft>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function preview() {
    setBusy(true);
    setError("");
    try {
      setResult(
        await api<Draft>("/ai/listing-assistant", {
          method: "POST",
          body: JSON.stringify({ message: notes }),
        }),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="listing-assistant">
      <div className="eyebrow">
        <Sparkles size={15} /> LISTING ASSISTANT
      </div>
      <h3>Start with what you know.</h3>
      <p>
        Turn your vehicle notes into a suggested draft. Review every detail
        before applying.
      </p>
      <label>
        Vehicle notes
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          maxLength={2000}
          placeholder="2026 Range Rover Sport SUV in Dubai, AED 850 per day, 5 seats, automatic, leather seats…"
        />
      </label>
      <button
        type="button"
        className="button dark"
        disabled={busy || notes.trim().length < 5}
        onClick={preview}
      >
        {busy ? "Preparing suggestions…" : "Preview suggestions"}
        <Sparkles size={14} />
      </button>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {result && (
        <div className="assistant-preview" aria-live="polite">
          <h3>Review your suggested details</h3>
          <dl>
            {Object.entries(result.suggestions).map(([key, value]) => (
              <div key={key}>
                <dt>{key.replaceAll("_", " ")}</dt>
                <dd>
                  {Array.isArray(value) ? value.join(", ") : String(value)}
                </dd>
              </div>
            ))}
          </dl>
          {result.missing_fields.length > 0 && (
            <p>
              Still needed:{" "}
              {result.missing_fields.join(", ").replaceAll("_", " ")}.
            </p>
          )}
          {result.warnings.map((w) => (
            <p key={w} className="fineprint">
              {w}
            </p>
          ))}
          <button
            type="button"
            className="button dark"
            onClick={() => {
              onApply(result.suggestions);
              setResult(undefined);
            }}
          >
            Apply suggestions to draft
            <Check size={15} />
          </button>
          <p className="fineprint">
            {result.mode === "deterministic"
              ? "Rules-based assistance · no language model connected. "
              : ""}
            Applying suggestions does not save or publish your listing.
          </p>
        </div>
      )}
    </div>
  );
}
