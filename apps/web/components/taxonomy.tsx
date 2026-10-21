"use client";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
type Item = {
  id: number;
  name: string;
  kind?: string;
  parent_id?: number | null;
  active?: boolean;
  brand_id?: number;
};
const resources = ["locations", "brands", "models", "categories"] as const;
export function Taxonomy() {
  const [resource, setResource] =
    useState<(typeof resources)[number]>("locations");
  const [rows, setRows] = useState<Item[]>([]);
  const [locations, setLocations] = useState<Item[]>([]);
  const [brands, setBrands] = useState<Item[]>([]);
  const [editing, setEditing] = useState<Item>();
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const load = useCallback(async () => {
    setBusy(true);
    setError("");
    try {
      const [data, loc, br] = await Promise.all([
        api<{ items: Item[] }>(`/admin/taxonomy/${resource}`),
        api<{ items: Item[] }>("/admin/taxonomy/locations"),
        api<{ items: Item[] }>("/admin/taxonomy/brands"),
      ]);
      setRows(data.items);
      setLocations(loc.items);
      setBrands(br.items);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }, [resource]);
  useEffect(() => {
    load();
  }, [load]);
  async function save(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fields = Object.fromEntries(new FormData(e.currentTarget));
    const body = {
      name: fields.name,
      ...(resource === "locations"
        ? {
            kind: fields.kind,
            parent_id: fields.parent_id ? Number(fields.parent_id) : null,
            active: fields.active === "on",
          }
        : {}),
      ...(resource === "models" ? { brand_id: Number(fields.brand_id) } : {}),
    };
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api(
        `/admin/taxonomy/${resource}${editing?.id ? `/${editing.id}` : ""}`,
        { method: editing?.id ? "PUT" : "POST", body: JSON.stringify(body) },
      );
      setEditing(undefined);
      setNotice("Catalog reference saved.");
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div>
      <div className="section-heading">
        <div>
          <div className="eyebrow">MARKETPLACE REFERENCE DATA</div>
          <h2>Shape the collection.</h2>
        </div>
        <button
          className="button dark"
          onClick={() =>
            setEditing({ id: 0, name: "", kind: "city", active: true })
          }
        >
          Add {resource === "categories" ? "category" : resource.slice(0, -1)}
        </button>
      </div>
      <div className="portal-tabs">
        {resources.map((r) => (
          <button
            key={r}
            className={r === resource ? "active" : ""}
            onClick={() => {
              setResource(r);
              setEditing(undefined);
              setNotice("");
            }}
          >
            {r}
          </button>
        ))}
      </div>
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
      {editing && (
        <div className="panel taxonomy-editor">
          <h3>
            {editing.id ? "Edit" : "Create"}{" "}
            {resource === "categories" ? "category" : resource.slice(0, -1)}
          </h3>
          <form key={`${resource}-${editing.id}`} onSubmit={save}>
            <div className="editor-grid">
              <label>
                Name
                <input
                  name="name"
                  defaultValue={editing.name}
                  required
                  minLength={1}
                  maxLength={80}
                />
              </label>
              {resource === "locations" && (
                <>
                  <label>
                    Location type
                    <select name="kind" defaultValue={editing.kind}>
                      {["country", "state", "city", "area", "airport"].map(
                        (k) => (
                          <option key={k}>{k}</option>
                        ),
                      )}
                    </select>
                  </label>
                  <label>
                    Parent location
                    <select
                      name="parent_id"
                      defaultValue={editing.parent_id || ""}
                    >
                      <option value="">None (country only)</option>
                      {locations
                        .filter((l) => l.id !== editing.id)
                        .map((l) => (
                          <option key={l.id} value={l.id}>
                            {l.name} · {l.kind}
                          </option>
                        ))}
                    </select>
                  </label>
                </>
              )}
              {resource === "models" && (
                <label>
                  Brand
                  <select
                    name="brand_id"
                    defaultValue={editing.brand_id || ""}
                    required
                  >
                    <option value="">Choose a brand</option>
                    {brands.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.name}
                      </option>
                    ))}
                  </select>
                </label>
              )}
            </div>
            {resource === "locations" && (
              <label className="checkbox">
                <input
                  type="checkbox"
                  name="active"
                  defaultChecked={editing.active}
                />{" "}
                Active marketplace location
              </label>
            )}
            <div className="modal-actions">
              <button type="button" onClick={() => setEditing(undefined)}>
                Cancel
              </button>
              <button className="button dark" disabled={busy}>
                Save reference
              </button>
            </div>
            <p className="fineprint">
              Changes affect catalog filtering. Parent relationships and
              references are validated by the marketplace.
            </p>
          </form>
        </div>
      )}
      <div className="records">
        {busy && !rows.length ? (
          <p className="empty">Loading reference data…</p>
        ) : (
          rows.map((row) => (
            <article className="record" key={row.id}>
              <div>
                <div className="eyebrow">
                  #{row.id} {row.kind || resource}
                </div>
                <h3>{row.name}</h3>
                {resource === "locations" && (
                  <p>
                    {row.parent_id
                      ? `Within ${locations.find((l) => l.id === row.parent_id)?.name || row.parent_id}`
                      : "Country root"}{" "}
                    · {row.active ? "Active" : "Inactive"}
                  </p>
                )}
                {resource === "models" && (
                  <p>{brands.find((b) => b.id === row.brand_id)?.name}</p>
                )}
              </div>
              <button onClick={() => setEditing(row)}>Edit</button>
            </article>
          ))
        )}
      </div>
    </div>
  );
}
