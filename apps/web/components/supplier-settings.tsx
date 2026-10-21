"use client";
import { FormEvent, useEffect, useState } from "react";
import { api } from "@/lib/api";

type Colleague = { id: number; email: string; role: string };
export function SupplierSettings({ userId }: { userId: number }) {
  const [cities, setCities] = useState<{ id: number; name: string }[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const [team, setTeam] = useState<Colleague[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    Promise.all([
      api<{ id: number; name: string; kind: string; active: boolean }[]>(
        "/locations",
      ),
      api<{ location_ids: number[] }>("/supplier/service-areas"),
      api<{ items: Colleague[] }>("/supplier/team"),
    ])
      .then(([locations, areas, colleagues]) => {
        setCities(locations.filter((x) => x.kind === "city" && x.active));
        setSelected(areas.location_ids);
        setTeam(colleagues.items);
      })
      .catch((e) => setError(e.message));
  }, []);
  async function saveAreas(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api("/supplier/service-areas", {
        method: "PUT",
        body: JSON.stringify({ location_ids: selected }),
      });
      setNotice("Service areas saved.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function addColleague(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api("/supplier/team", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      setTeam((await api<{ items: Colleague[] }>("/supplier/team")).items);
      form.reset();
      setNotice(
        "Colleague account created. Share the demo sign-in details directly.",
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="supplier-settings">
      <h3>Locations you serve</h3>
      <p className="fineprint">
        Choose active rental cities. Pause published offers before removing
        their city.
      </p>
      <form onSubmit={saveAreas}>
        <div className="feature-list">
          {cities.map((city) => (
            <label className="checkbox" key={city.id}>
              <input
                type="checkbox"
                checked={selected.includes(city.id)}
                onChange={(e) =>
                  setSelected(
                    e.target.checked
                      ? [...selected, city.id]
                      : selected.filter((id) => id !== city.id),
                  )
                }
              />
              Serve {city.name}
            </label>
          ))}
        </div>
        <button className="button dark" disabled={busy}>
          Save service areas
        </button>
      </form>
      <h3 className="settings-heading">Your authorized colleagues</h3>
      <p className="fineprint">
        Each colleague receives their own account and can access only this
        supplier’s marketplace records.
      </p>
      {team.map((person) => (
        <p key={person.id}>
          {person.email} <span className="status">{person.role}</span>
        </p>
      ))}
      {team.some(
        (person) => person.id === userId && person.role === "owner",
      ) && (
        <form onSubmit={addColleague} className="profile-form">
          <label>
            Colleague email
            <input name="email" type="email" required autoComplete="off" />
          </label>
          <label>
            Colleague demo password
            <input
              name="password"
              type="password"
              minLength={10}
              maxLength={128}
              required
              autoComplete="new-password"
            />
          </label>
          <button className="button dark" disabled={busy}>
            Create colleague account
          </button>
          <p className="fineprint">
            Demonstration accounts only. This action does not send an invitation
            email.
          </p>
        </form>
      )}
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      {notice && (
        <p className="notice" role="status">
          {notice}
        </p>
      )}
    </div>
  );
}
