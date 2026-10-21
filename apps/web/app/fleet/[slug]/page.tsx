"use client";
import { use, useEffect, useState, FormEvent } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowUpRight,
  Check,
  MapPin,
  Users,
  Gauge,
  ShieldCheck,
} from "lucide-react";
import { api, Listing, mediaUrl, price } from "@/lib/api";
import { VehicleImage, VehicleCard } from "@/components/vehicle";
export default function Detail({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const [car, setCar] = useState<Listing>();
  const [related, setRelated] = useState<Listing[]>([]);
  const [activeImage, setActiveImage] = useState(0);
  const [error, setError] = useState("");
  const [sent, setSent] = useState<number>();
  const [busy, setBusy] = useState(false);
  const [inquiryError, setInquiryError] = useState("");
  useEffect(() => {
    setCar(undefined);
    setRelated([]);
    setSent(undefined);
    setError("");
    setActiveImage(0);
    api<Listing>(`/listings/${slug}`)
      .then((listing) => {
        setCar(listing);
        api<{ items: Listing[] }>(
          `/listings?city=${encodeURIComponent(listing.city)}&category=${encodeURIComponent(listing.category)}&page_size=4`,
        )
          .then((result) =>
            setRelated(
              result.items.filter((item) => item.id !== listing.id).slice(0, 3),
            ),
          )
          .catch(() => setRelated([]));
      })
      .catch((e) => setError(e.message));
  }, [slug]);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    if (
      form.get("end_date") &&
      String(form.get("end_date")) < String(form.get("start_date"))
    ) {
      setInquiryError("The end date must be after the start date.");
      return;
    }
    setBusy(true);
    setInquiryError("");
    try {
      const result = await api<{ id: number }>("/leads", {
        method: "POST",
        body: JSON.stringify({
          ...Object.fromEntries(form),
          listing_id: car!.id,
          source: "website",
          start_date: form.get("start_date") || null,
          end_date: form.get("end_date") || null,
        }),
      });
      setSent(result.id);
    } catch (e) {
      setInquiryError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (error)
    return (
      <section className="section">
        <div className="error">{error}</div>
        <Link href="/fleet">Back to fleet</Link>
      </section>
    );
  if (!car)
    return <section className="section">Preparing your vehicle…</section>;
  return (
    <section className="section detail-page">
      <Link className="text-link" href="/fleet">
        <ArrowLeft size={16} /> Back to the collection
      </Link>
      <div className="detail-heading">
        <div>
          <div className="eyebrow">
            {car.category} · {car.year} {car.trim ? `· ${car.trim}` : ""}{" "}
            {car.vehicle_type ? `· ${car.vehicle_type}` : ""}
          </div>
          <h1>
            {car.brand} <em>{car.model}</em>
          </h1>
          <p>
            <MapPin size={16} /> {car.city}, {car.country} <span>·</span>{" "}
            Offered by {car.supplier_name}
          </p>
        </div>
        <div className="price-large">
          {price(car.daily_price, car.currency)}
          <small>per day · indicative rental rate</small>
        </div>
      </div>
      <div className="detail-grid">
        <div>
          <div className="detail-image">
            <VehicleImage
              listing={
                car.images?.length
                  ? {
                      ...car,
                      images: [car.images[activeImage] || car.images[0]],
                    }
                  : car
              }
            />
          </div>
          {car.images?.length > 1 && (
            <div className="gallery">
              {car.images.map((im, i) => (
                <button
                  type="button"
                  key={im}
                  aria-label={`Show vehicle photo ${i + 1}`}
                  aria-pressed={activeImage === i}
                  onClick={() => setActiveImage(i)}
                >
                  <img
                    src={mediaUrl(im)}
                    alt={`${car.brand} ${car.model}, view ${i + 1}`}
                  />
                </button>
              ))}
            </div>
          )}
          <div className="detail-specs">
            <span>
              <Users />
              {car.seats} passengers
            </span>
            <span>
              <Gauge />
              {car.transmission}
            </span>
            <span>
              <ShieldCheck />
              Approved listing
            </span>
          </div>
          <h2>A closer look.</h2>
          <p className="description">{car.description}</p>
          <div className="feature-list">
            {car.features?.map((f) => (
              <span key={f}>
                <Check size={15} />
                {f}
              </span>
            ))}
          </div>
          <div className="rate-grid">
            {[
              ["Daily", car.daily_price],
              ["Weekly", car.weekly_price],
              ["Monthly", car.monthly_price],
            ].map(([label, value]) => (
              <div key={String(label)}>
                <small>{label} rate</small>
                <strong>
                  {price(value as number | undefined, car.currency)}
                </strong>
              </div>
            ))}
          </div>
          <p className="fineprint">
            Refundable deposit:{" "}
            {car.deposit != null
              ? price(car.deposit, car.currency)
              : "Confirm with supplier"}
            . Mileage allowance: {car.mileage || "Confirm with supplier"}.
            Additional charges and availability are confirmed directly by the
            supplier.
          </p>
        </div>
        <aside className="inquiry-panel">
          {sent ? (
            <div role="status" className="success">
              <Check size={36} />
              <h2>Your inquiry is in.</h2>
              <p>
                Reference #{sent}. Your request has been saved for the supplier.
                This is an inquiry, not a confirmed reservation.
              </p>
              <Link href="/fleet" className="button dark">
                Explore more cars <ArrowUpRight size={16} />
              </Link>
              <p>
                <a
                  className="text-link"
                  href={`https://wa.me/?text=${encodeURIComponent(`Quote inquiry #${sent}: ${car.brand} ${car.model} in ${car.city}. Please confirm final pricing and availability. This is a demonstration inquiry.`)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Continue in WhatsApp <ArrowUpRight size={14} />
                </a>
              </p>
              <p className="fineprint">
                Choose the recipient yourself. No message is sent automatically
                and no real company number is preselected.
              </p>
            </div>
          ) : (
            <>
              <div className="eyebrow">YOUR NEXT GREAT DRIVE</div>
              <h2>Make it happen.</h2>
              <p>Share a few details to request a quote from the supplier.</p>
              <form onSubmit={submit}>
                <label>
                  Full name
                  <input
                    name="name"
                    required
                    minLength={2}
                    placeholder="Your name"
                  />
                </label>
                <label>
                  Email address
                  <input
                    type="email"
                    name="email"
                    required
                    placeholder="you@example.com"
                  />
                </label>
                <label>
                  Phone number
                  <input
                    type="tel"
                    name="phone"
                    required
                    minLength={6}
                    placeholder="+971 …"
                  />
                </label>
                <div className="form-row">
                  <label>
                    From
                    <input
                      type="date"
                      name="start_date"
                      min={new Date().toISOString().slice(0, 10)}
                    />
                  </label>
                  <label>
                    Until
                    <input
                      type="date"
                      name="end_date"
                      min={new Date().toISOString().slice(0, 10)}
                    />
                  </label>
                </div>
                <label>
                  Your plans
                  <textarea
                    name="message"
                    required
                    minLength={5}
                    rows={3}
                    placeholder="Tell us about your trip…"
                  />
                </label>
                <label className="checkbox">
                  <input type="checkbox" required /> I agree to share these
                  details with the rental supplier for this inquiry.
                </label>
                <p className="fineprint">
                  Demonstration only. Please use fictional contact details.
                </p>
                {inquiryError && (
                  <div role="alert" className="error">
                    {inquiryError}
                  </div>
                )}
                <button className="button dark full" disabled={busy}>
                  {busy ? "Saving your inquiry…" : "Request a quote"}
                  <ArrowUpRight size={16} />
                </button>
                <p className="fineprint">
                  No payment required. Availability is subject to supplier
                  confirmation.
                </p>
              </form>
            </>
          )}
        </aside>
      </div>
      {related.length > 0 && (
        <div className="related-vehicles">
          <div className="section-heading">
            <div>
              <div className="eyebrow">MORE TO CONSIDER</div>
              <h2>Another direction.</h2>
            </div>
          </div>
          <div className="vehicle-grid">
            {related.map((listing) => (
              <VehicleCard key={listing.id} listing={listing} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
