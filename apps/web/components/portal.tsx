"use client";
import { FormEvent, useCallback, useEffect, useState } from "react";
import {
  ArrowUpRight,
  Plus,
  LogOut,
  Check,
  Upload,
  ChevronRight,
} from "lucide-react";
import { api, User, price, mediaUrl } from "@/lib/api";
import { ListingAssistant } from "@/components/listing-assistant";
import { Insights } from "@/components/insights";
import { Taxonomy } from "@/components/taxonomy";
import { prepareUploadImage } from "@/lib/upload-image";
import { SupplierSettings } from "@/components/supplier-settings";
type Row = Record<string, unknown>;
const blank = {
  brand: "",
  model: "",
  year: 2026,
  trim: "",
  vehicle_type: "SUV",
  city: "Dubai",
  country: "UAE",
  category: "SUV",
  categories: "",
  currency: "AED",
  daily_price: 0,
  weekly_price: "",
  monthly_price: "",
  seats: 5,
  transmission: "Automatic",
  description: "",
  features: "",
  images: [] as string[],
  deposit: "",
  mileage: "250",
};
export function Portal({ admin = false }: { admin?: boolean }) {
  const [user, setUser] = useState<User>();
  const [register, setRegister] = useState(false);
  const [tab, setTab] = useState(admin ? "listings" : "overview");
  const [rows, setRows] = useState<Row[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [counts, setCounts] = useState<Record<string, number>>();
  const [profile, setProfile] = useState<Row>({});
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [editor, setEditor] = useState<typeof blank>();
  const [editId, setEditId] = useState<number>();
  const [action, setAction] = useState<{
    path: string;
    title: string;
    reason: boolean;
  }>();
  const prefix = admin ? "/admin" : "/supplier";
  useEffect(() => {
    api<User>("/auth/me")
      .then(setUser)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  const reload = useCallback(async () => {
    if (!user) return;
    setError("");
    try {
      if (!admin) {
        setProfile(await api<Row>("/supplier/profile"));
        const insights = await api<{
          listings_by_status: Record<string, number>;
        }>("/ai/marketplace-insights");
        setCounts(insights.listings_by_status);
      }
      const resource = tab === "overview" ? "listings" : tab;
      if (!["profile", "insights", "taxonomy"].includes(resource)) {
        const d = await api<{ items: Row[]; total: number }>(
          `${prefix}/${resource}?page=${page}&page_size=24`,
        );
        setRows(d.items);
        setTotal(d.total);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }, [user, admin, tab, page, prefix]);
  useEffect(() => {
    reload();
  }, [reload]);
  async function login(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const d = Object.fromEntries(new FormData(e.currentTarget));
      const result = await api<{ access_token: string; user: User }>(
        register ? "/auth/register" : "/auth/login",
        { method: "POST", body: JSON.stringify(d) },
      );
      localStorage.setItem("lavish_token", result.access_token);
      setUser(result.user);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function mutate(path: string, body?: unknown, method = "POST") {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api(path, {
        method,
        body: body ? JSON.stringify(body) : undefined,
      });
      setNotice("Saved successfully.");
      await reload();
      return true;
    } catch (e) {
      setError((e as Error).message);
      return false;
    } finally {
      setBusy(false);
    }
  }
  async function saveListing(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!editor) return;
    const payload = {
      ...Object.fromEntries(
        Object.keys(blank).map((k) => [k, editor[k as keyof typeof blank]]),
      ),
      mileage: Number(editor.mileage),
      features: editor.features
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      categories: editor.categories
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      weekly_price:
        editor.weekly_price === "" ? null : Number(editor.weekly_price),
      monthly_price:
        editor.monthly_price === "" ? null : Number(editor.monthly_price),
      deposit: editor.deposit === "" ? null : Number(editor.deposit),
    };
    if (
      await mutate(
        editId ? `${prefix}/listings/${editId}` : "/supplier/listings",
        payload,
        editId ? "PUT" : "POST",
      )
    )
      setEditor(undefined);
  }
  async function upload(files: FileList | null) {
    if (!editor || !files) return;
    if (editor.images.length + files.length > 10) {
      setError("A listing can have up to 10 images.");
      return;
    }
    setBusy(true);
    setError("");
    const urls = [...editor.images];
    try {
      for (const file of Array.from(files)) {
        if (
          !["image/jpeg", "image/png", "image/webp"].includes(file.type) ||
          file.size > 8 * 1024 * 1024
        )
          throw Error("Use JPG, PNG or WebP images, up to 8 MB each.");
        const fd = new FormData();
        fd.append("file", await prepareUploadImage(file));
        const d = await api<{
          url: string;
          quality?: { warnings: string[]; cover_candidate_score: number };
        }>("/supplier/uploads", {
          method: "POST",
          body: fd,
        });
        urls.push(d.url);
        if (d.quality)
          setNotice(
            `Photo checks: cover candidate score ${d.quality.cover_candidate_score}/100. ${d.quality.warnings.join(" ") || "No basic quality warnings. Review the actual photo before publishing."}`,
          );
      }
      setEditor({ ...editor, images: urls });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function edit(row: Row) {
    setEditId(Number(row.id));
    setEditor({
      ...blank,
      ...row,
      features: ((row.features || []) as string[]).join(", "),
      categories: ((row.categories || []) as string[]).join(", "),
      weekly_price: row.weekly_price == null ? "" : String(row.weekly_price),
      monthly_price: row.monthly_price == null ? "" : String(row.monthly_price),
      deposit: row.deposit == null ? "" : String(row.deposit),
    } as typeof blank);
  }
  if (loading)
    return <section className="section">Opening your workspace…</section>;
  if (!user)
    return (
      <section className="auth-page">
        <div className="auth-intro">
          <div className="eyebrow">
            {admin ? "LAVISHCARS OPERATIONS" : "THE PARTNER NETWORK"}
          </div>
          <h1>
            {admin ? "A considered" : "Extraordinary cars."}
            <br />
            <em>{admin ? "marketplace." : "Exceptional partners."}</em>
          </h1>
          <p>
            {admin
              ? "Review suppliers, curate the collection, and keep every inquiry moving."
              : "Your workspace for vehicles, approvals, and customer inquiries. A clear path from your fleet to their next journey."}
          </p>
          <div className="workflow">
            <span>01 Register</span>
            <ChevronRight />
            <span>02 List</span>
            <ChevronRight />
            <span>03 Get approved</span>
          </div>
        </div>
        <div className="auth-card">
          <h2>
            {register
              ? "Become a partner."
              : admin
                ? "Admin sign in."
                : "Welcome back."}
          </h2>
          <p>
            {register
              ? "Create your supplier account to get started."
              : "Sign in to your marketplace workspace."}
          </p>
          <form onSubmit={login}>
            {register && (
              <label>
                Company name
                <input name="company_name" required minLength={2} />
              </label>
            )}
            <label>
              Email address
              <input
                name="email"
                type="email"
                required
                defaultValue={
                  admin ? "admin@lavish.demo" : "supplier@lavish.demo"
                }
              />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                minLength={10}
                required
                defaultValue={
                  process.env.NODE_ENV === "development" ? "DemoDrive!2026" : ""
                }
              />
            </label>
            {error && (
              <div role="alert" className="error">
                {error}
              </div>
            )}
            <button className="button dark full" disabled={busy}>
              {busy ? "Please wait…" : register ? "Create account" : "Sign in"}
              <ArrowUpRight size={16} />
            </button>
          </form>
          {!admin && (
            <button
              className="text-link"
              onClick={() => setRegister(!register)}
            >
              {register
                ? "Already a partner? Sign in"
                : "New to LavishCars? Create an account"}
            </button>
          )}
          <p className="fineprint">
            Local demo credentials are prefilled. Use fictional details only.
            New supplier accounts require administrator approval.
          </p>
        </div>
      </section>
    );
  if (admin && user.role !== "admin")
    return (
      <section className="section">
        <h1>Administrator access required.</h1>
        <button
          className="button dark"
          onClick={() => {
            api("/auth/logout", { method: "POST" }).catch(() => {});
            localStorage.removeItem("lavish_token");
            setUser(undefined);
          }}
        >
          Sign in with an administrator account
        </button>
      </section>
    );
  return (
    <section className="section portal">
      <div className="section-heading">
        <div>
          <div className="eyebrow">
            {admin ? "OPERATIONS CONSOLE" : "PARTNER WORKSPACE"}
          </div>
          <h1>
            {admin
              ? "A higher standard."
              : String(profile.company_name || "Your fleet. Your future.")}
          </h1>
          <p className="muted">
            {user.email}{" "}
            {!admin && (
              <>
                · Supplier status:{" "}
                <span className={`status ${profile.status}`}>
                  {String(profile.status || "pending")}
                </span>
              </>
            )}
          </p>
        </div>
        <button
          className="text-link"
          onClick={() => {
            api("/auth/logout", { method: "POST" }).catch(() => {});
            localStorage.removeItem("lavish_token");
            setUser(undefined);
          }}
        >
          <LogOut size={15} /> Sign out
        </button>
      </div>
      <div className="portal-tabs">
        {(admin
          ? [
              "listings",
              "suppliers",
              "leads",
              "insights",
              "taxonomy",
              "audit-logs",
            ]
          : ["overview", "listings", "leads", "insights", "profile"]
        ).map((t) => (
          <button
            key={t}
            className={tab === t ? "active" : ""}
            onClick={() => {
              setTab(t);
              setPage(1);
              setEditor(undefined);
            }}
          >
            {t.replace("-", " ")}
          </button>
        ))}
      </div>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="notice" role="status">
          <Check size={16} />
          {notice}
        </div>
      )}
      {tab === "insights" ? (
        <Insights />
      ) : tab === "taxonomy" && admin ? (
        <Taxonomy />
      ) : tab === "profile" ? (
        <div className="panel">
          <h2>Your company profile.</h2>
          <p className="muted">
            Keep your company and verification information up to date.
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              mutate(
                "/supplier/profile",
                Object.fromEntries(new FormData(e.currentTarget)),
                "PUT",
              );
            }}
            className="profile-form"
          >
            {[
              ["company_name", "Company name"],
              ["contact_email", "Contact email"],
              ["phone", "Phone"],
              ["license_number", "Trade licence number"],
            ].map(([key, label]) => (
              <label key={`${key}-${profile[key]}`}>
                {label}
                <input
                  name={key}
                  required={key === "company_name"}
                  defaultValue={String(profile[key] || "")}
                />
              </label>
            ))}
            <button className="button dark" disabled={busy}>
              Save profile
            </button>
          </form>
          <SupplierSettings userId={user.id} />
        </div>
      ) : editor ? (
        <div className="panel listing-editor">
          <div className="section-heading">
            <div>
              <div className="eyebrow">DRAFT → REVIEW → PUBLISHED</div>
              <h2>
                {editId ? "Refine your listing." : "Introduce your vehicle."}
              </h2>
            </div>
            <button className="text-link" onClick={() => setEditor(undefined)}>
              Cancel
            </button>
          </div>
          <p className="fineprint">
            {admin
              ? "Review every specification and price before saving. Administrative edits are recorded in the audit history."
              : "Material edits to a published vehicle require renewed review. New listings are saved as drafts; submit for review when ready."}
          </p>
          {!admin && (
            <ListingAssistant
              onApply={(suggestions) => {
                const valid = Object.fromEntries(
                  Object.entries(suggestions).filter(
                    ([key]) => key in blank && key !== "images",
                  ),
                );
                setEditor({
                  ...editor,
                  ...valid,
                  features: Array.isArray(valid.features)
                    ? valid.features.join(", ")
                    : editor.features,
                } as typeof blank);
              }}
            />
          )}
          <form onSubmit={saveListing}>
            <div className="editor-grid">
              {[
                ["brand", "Brand", "text"],
                ["model", "Model", "text"],
                ["year", "Year", "number"],
                ["trim", "Trim (optional)", "text"],
                ["vehicle_type", "Vehicle type", "text"],
                ["city", "City", "text"],
                ["country", "Country (UAE / USA)", "text"],
                ["category", "Category", "text"],
                [
                  "categories",
                  "Additional categories (comma separated)",
                  "text",
                ],
                ["currency", "Currency (AED / USD)", "text"],
                ["daily_price", "Daily rate", "number"],
                ["weekly_price", "Weekly rate (optional)", "number"],
                ["monthly_price", "Monthly rate (optional)", "number"],
                ["seats", "Seats", "number"],
                ["transmission", "Transmission", "text"],
                ["deposit", "Deposit (optional)", "number"],
                ["mileage", "Daily mileage allowance (km)", "number"],
              ].map(([key, label, type]) => (
                <label key={key}>
                  {label}
                  <input
                    type={type}
                    min={type === "number" ? 0 : undefined}
                    step={type === "number" ? "any" : undefined}
                    required={[
                      "brand",
                      "model",
                      "city",
                      "country",
                      "category",
                      "currency",
                      "daily_price",
                    ].includes(key)}
                    value={String(editor[key as keyof typeof editor])}
                    onChange={(e) =>
                      setEditor({
                        ...editor,
                        [key]: ["year", "daily_price", "seats"].includes(key)
                          ? Number(e.target.value)
                          : e.target.value,
                      })
                    }
                  />
                </label>
              ))}
            </div>
            <label>
              Description
              <textarea
                required
                minLength={20}
                rows={4}
                value={editor.description}
                onChange={(e) =>
                  setEditor({ ...editor, description: e.target.value })
                }
              />
            </label>
            <label>
              Features, separated by commas
              <input
                value={editor.features}
                onChange={(e) =>
                  setEditor({ ...editor, features: e.target.value })
                }
                placeholder="Bluetooth, Leather seats, Parking camera"
              />
            </label>
            {!admin && (
              <div className="upload-area">
                <Upload size={24} />
                <label>
                  Vehicle photography
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    multiple
                    onChange={(e) => upload(e.target.files)}
                    disabled={busy}
                  />
                </label>
                <small>
                  Up to 10 photos · JPG, PNG, WebP · 8 MB per original. Large
                  photos are resized and compressed for upload.
                </small>
              </div>
            )}
            <div className="upload-grid">
              {editor.images.map((url, i) => (
                <div key={url}>
                  <img src={mediaUrl(url)} alt={`Vehicle upload ${i + 1}`} />
                  <div>
                    <button
                      type="button"
                      disabled={!i}
                      onClick={() => {
                        const images = [...editor.images];
                        [images[i - 1], images[i]] = [images[i], images[i - 1]];
                        setEditor({ ...editor, images });
                      }}
                    >
                      Move earlier
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        setEditor({
                          ...editor,
                          images: editor.images.filter((_, n) => n !== i),
                        })
                      }
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <button className="button dark" disabled={busy}>
              {busy ? "Saving…" : admin ? "Save listing changes" : "Save draft"}
              <Check size={17} />
            </button>
          </form>
        </div>
      ) : (
        <>
          {!admin && (tab === "overview" || tab === "listings") && (
            <>
              <div className="stats-row">
                <div>
                  <small>Your vehicles</small>
                  <strong>
                    {counts
                      ? Object.values(counts).reduce((sum, n) => sum + n, 0)
                      : "…"}
                  </strong>
                </div>
                <div>
                  <small>Published</small>
                  <strong>{counts ? counts.published || 0 : "…"}</strong>
                </div>
                <div>
                  <small>Awaiting review</small>
                  <strong>{counts ? counts.pending || 0 : "…"}</strong>
                </div>
                <div>
                  <small>Drafts</small>
                  <strong>{counts ? counts.draft || 0 : "…"}</strong>
                </div>
              </div>
              <div className="section-heading">
                <h2>Your collection.</h2>
                <button
                  className="button dark"
                  onClick={() => {
                    setEditId(undefined);
                    setEditor({ ...blank });
                  }}
                >
                  <Plus size={16} /> Add vehicle
                </button>
              </div>
            </>
          )}
          <div className="records">
            {rows.length ? (
              rows.map((row, i) => (
                <article className="record" key={String(row.id || i)}>
                  <div className="record-main">
                    {tab === "leads" ? (
                      <>
                        <div className="eyebrow">
                          INQUIRY #{String(row.id)} ·{" "}
                          {String(row.source || "web")}
                        </div>
                        <h3>{String(row.name || "Customer inquiry")}</h3>
                        <p>
                          {String(row.email)} · {String(row.phone)}
                        </p>
                        <p>{String(row.message)}</p>
                        <small>
                          Vehicle #{String(row.listing_id)} ·{" "}
                          {String(row.start_date || "Dates to confirm")}{" "}
                          {row.end_date ? `to ${row.end_date}` : ""}
                        </small>
                      </>
                    ) : tab === "suppliers" ? (
                      <>
                        <div className="eyebrow">
                          SUPPLIER #{String(row.id)}
                        </div>
                        <h3>{String(row.company_name)}</h3>
                        <p>
                          {String(row.contact_email || "")} ·{" "}
                          {String(row.phone || "")}
                        </p>
                        <small>
                          Licence:{" "}
                          {String(row.license_number || "Not provided")}
                        </small>
                      </>
                    ) : tab === "audit-logs" ? (
                      <>
                        <div className="eyebrow">
                          {String(row.created_at || "")}
                        </div>
                        <h3>{String(row.action || "Audit event")}</h3>
                        <pre>{JSON.stringify(row, null, 2)}</pre>
                      </>
                    ) : (
                      <>
                        <div className="eyebrow">
                          {String(row.city)} · {String(row.year)}
                        </div>
                        <h3>
                          {String(row.brand)} {String(row.model)}
                        </h3>
                        <p>
                          {price(Number(row.daily_price), String(row.currency))}{" "}
                          / day{" "}
                          <span>
                            ·{" "}
                            {String(
                              row.supplier_name || profile.company_name || "",
                            )}
                          </span>
                        </p>
                        {Boolean(row.rejection_reason) && (
                          <p className="rejection">
                            Review note: {String(row.rejection_reason)}
                          </p>
                        )}
                      </>
                    )}
                  </div>
                  <div className="record-actions">
                    {Boolean(row.status) && (
                      <span className={`status ${row.status}`}>
                        {String(row.status).replaceAll("_", " ")}
                      </span>
                    )}
                    {tab === "leads" ? (
                      <select
                        aria-label={`Status for inquiry ${row.id}`}
                        value={String(row.status)}
                        disabled={busy}
                        onChange={(e) =>
                          mutate(
                            `${prefix}/leads/${row.id}`,
                            { status: e.target.value },
                            "PATCH",
                          )
                        }
                      >
                        {["new", "contacted", "quoted", "booked", "lost"].map(
                          (s) => (
                            <option key={s}>{s}</option>
                          ),
                        )}
                      </select>
                    ) : tab === "audit-logs" ? null : admin ? (
                      <>
                        {tab === "listings" && row.status !== "archived" && (
                          <button onClick={() => edit(row)}>
                            Edit listing
                          </button>
                        )}
                        {(row.status === "pending" ||
                          (tab === "suppliers" &&
                            row.status !== "approved")) && (
                          <button
                            disabled={busy}
                            onClick={() =>
                              setAction({
                                path: `${prefix}/${tab}/${row.id}/approve`,
                                title: `Approve ${tab === "suppliers" ? row.company_name : `${row.brand} ${row.model}`}?`,
                                reason: false,
                              })
                            }
                          >
                            Approve
                          </button>
                        )}
                        {row.status === "pending" && (
                          <button
                            disabled={busy}
                            onClick={() =>
                              setAction({
                                path: `${prefix}/${tab}/${row.id}/reject`,
                                title: "Reject with a review note",
                                reason: true,
                              })
                            }
                          >
                            Reject
                          </button>
                        )}
                        {tab === "listings" && row.status === "published" && (
                          <button
                            disabled={busy}
                            onClick={() =>
                              setAction({
                                path: `${prefix}/listings/${row.id}/${row.admin_hidden ? "unhide" : "hide"}`,
                                title: row.admin_hidden
                                  ? "Make this listing visible again?"
                                  : "Hide this listing from the marketplace?",
                                reason: true,
                              })
                            }
                          >
                            {row.admin_hidden
                              ? "Restore visibility"
                              : "Hide listing"}
                          </button>
                        )}
                        {tab === "suppliers" && row.status !== "suspended" && (
                          <button
                            disabled={busy}
                            onClick={() =>
                              setAction({
                                path: `${prefix}/suppliers/${row.id}/suspend`,
                                title: `Suspend ${row.company_name}? Its vehicles will be hidden.`,
                                reason: true,
                              })
                            }
                          >
                            Suspend
                          </button>
                        )}
                      </>
                    ) : (
                      <>
                        {row.status !== "archived" && (
                          <button onClick={() => edit(row)}>Edit</button>
                        )}
                        {["draft", "rejected", "paused"].includes(
                          String(row.status),
                        ) && (
                          <button
                            disabled={busy}
                            onClick={() =>
                              mutate(`/supplier/listings/${row.id}/submit`)
                            }
                          >
                            Submit for review
                          </button>
                        )}
                        {row.status === "published" && (
                          <button
                            disabled={busy}
                            onClick={() =>
                              mutate(`/supplier/listings/${row.id}/pause`)
                            }
                          >
                            Pause
                          </button>
                        )}
                        {row.status !== "archived" && (
                          <button
                            onClick={() =>
                              setAction({
                                path: `/supplier/listings/${row.id}/archive`,
                                title: "Archive this vehicle?",
                                reason: false,
                              })
                            }
                          >
                            Archive
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </article>
              ))
            ) : (
              <div className="empty">
                <h3>
                  {tab === "leads"
                    ? "Your next conversation starts here."
                    : "A clean slate."}
                </h3>
                <p>
                  {tab === "leads"
                    ? "Customer inquiries will appear here after a visitor requests a quote."
                    : "No records to display yet."}
                </p>
              </div>
            )}
          </div>
          <div className="pagination" aria-label="Portal pagination">
            <button
              disabled={page === 1 || busy}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </button>
            <span>
              Page {page} of {Math.max(1, Math.ceil(total / 24))} · {total}{" "}
              records
            </span>
            <button
              disabled={page * 24 >= total || busy}
              onClick={() => setPage(page + 1)}
            >
              Next
            </button>
          </div>
          {tab === "leads" && (
            <p className="fineprint">
              “Booked” is a manually tracked CRM outcome. This prototype does
              not process reservations or payments.
            </p>
          )}
        </>
      )}
      {action && (
        <div className="modal-backdrop">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="action-title"
          >
            <h2 id="action-title">{action.title}</h2>
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                const data = Object.fromEntries(new FormData(e.currentTarget));
                if (await mutate(action.path, data)) setAction(undefined);
              }}
            >
              {action.reason && (
                <label>
                  Reason
                  <textarea
                    name="reason"
                    autoFocus
                    required
                    minLength={3}
                    rows={3}
                  />
                </label>
              )}
              <div className="modal-actions">
                <button type="button" onClick={() => setAction(undefined)}>
                  Cancel
                </button>
                <button className="button dark" disabled={busy}>
                  Confirm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}
