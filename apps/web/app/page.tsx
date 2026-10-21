"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  MapPin,
  Sparkles,
  ShieldCheck,
  MessagesSquare,
  SlidersHorizontal,
} from "lucide-react";
import { api, Listing } from "@/lib/api";
import { VehicleCard } from "@/components/vehicle";
export default function Home() {
  const [cars, setCars] = useState<Listing[]>([]);
  const [error, setError] = useState("");
  const [city, setCity] = useState("Dubai");
  useEffect(() => {
    api<{ items: Listing[] }>("/listings?page_size=3")
      .then((d) => setCars(d.items.slice(0, 3)))
      .catch((e) => setError(e.message));
  }, []);
  return (
    <>
      <section className="hero">
        <img
          className="hero-editorial"
          src="/images/hero-concept.webp"
          alt="AI-generated concept artwork of a grand touring coupe at sunset"
          fetchPriority="high"
        />
        <div className="hero-shade" aria-hidden="true" />
        <div className="hero-copy">
          <div className="eyebrow">
            <span className="gold-line" /> THE JOURNEY IS YOURS
          </div>
          <h1>
            Don’t just arrive.
            <br />
            <em>Make an entrance.</em>
          </h1>
          <p>
            A considered collection of extraordinary cars.
            <br />
            The right drive, for wherever life takes you.
          </p>
          <div className="hero-search">
            <div>
              <MapPin size={19} />
              <label htmlFor="hero-city">
                YOUR DESTINATION
                <select
                  id="hero-city"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                >
                  <option>Dubai</option>
                  <option>Houston</option>
                </select>
              </label>
            </div>
            <Link href={`/fleet?city=${city}`} className="button gold">
              Explore cars <ArrowUpRight size={18} />
            </Link>
          </div>
          <Link className="concierge-inline" href="/concierge">
            <Sparkles size={16} />
            <span>
              Not sure where to start? <b>Ask our AI concierge</b>
            </span>
            <ArrowRight size={16} />
          </Link>
        </div>
        <div className="hero-stage">
          <div className="hero-caption">
            <span>AN EXTRAORDINARY PERSPECTIVE</span>
            <strong>Your next chapter starts here.</strong>
            <small>AI-generated concept artwork · Illustrative vehicle</small>
          </div>
        </div>
        <div className="hero-bottom">
          <span>
            DUBAI <i /> HOUSTON <i /> BEYOND
          </span>
          <span>CURATED CARS. PERSONAL SERVICE.</span>
        </div>
      </section>
      <div className="trust-strip">
        <span>
          <ShieldCheck /> Approved supplier network
        </span>
        <span>
          <SlidersHorizontal /> Clear, upfront rental rates
        </span>
        <span>
          <MessagesSquare /> Connect directly with suppliers
        </span>
      </div>
      <section className="section">
        <div className="section-heading">
          <div>
            <div className="eyebrow">THE COLLECTION</div>
            <h2>Exceptional by choice.</h2>
          </div>
          <Link href="/fleet" className="text-link">
            Discover the full fleet <ArrowUpRight size={18} />
          </Link>
        </div>
        <div className="category-links">
          {["All cars", "SUV", "Sports", "Luxury", "Convertible"].map(
            (x, i) => (
              <Link
                key={x}
                className={i === 0 ? "active" : ""}
                href={i ? `/fleet?category=${x}` : "/fleet"}
              >
                {x}
              </Link>
            ),
          )}
        </div>
        {error ? (
          <div className="empty">
            <h3>The collection is taking a moment.</h3>
            <p>
              Start the marketplace API to view the live demonstration catalog.
            </p>
            <small>{error}</small>
          </div>
        ) : (
          <div className="vehicle-grid">
            {cars.length
              ? cars.map((car) => <VehicleCard key={car.id} listing={car} />)
              : [1, 2, 3].map((n) => <div className="skeleton" key={n} />)}
          </div>
        )}
      </section>
      <section className="concierge-banner">
        <div className="concierge-mark">
          <Sparkles size={35} />
        </div>
        <div>
          <div className="eyebrow">
            A LITTLE INTELLIGENCE. A LOT OF POSSIBILITY.
          </div>
          <h2>Your plans. Your perfect car.</h2>
          <p>
            Tell us about your trip. Our concierge will find the cars that fit.
          </p>
        </div>
        <Link className="button light" href="/concierge">
          Meet your concierge <ArrowUpRight size={18} />
        </Link>
      </section>
      <section className="section destinations">
        <div className="section-heading">
          <div>
            <div className="eyebrow">WHERE WILL YOU GO?</div>
            <h2>A city. A feeling. A drive.</h2>
          </div>
          <span className="muted">
            Two distinctive destinations. Endless possibilities.
          </span>
        </div>
        <div className="destination-grid">
          <Link href="/fleet?city=Dubai" className="destination dubai">
            <div className="skyline">
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
            </div>
            <div>
              <span>UNITED ARAB EMIRATES</span>
              <h3>
                Dubai <ArrowUpRight />
              </h3>
              <p>For a city that never settles for ordinary.</p>
            </div>
          </Link>
          <Link href="/fleet?city=Houston" className="destination houston">
            <div className="skyline">
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
            </div>
            <div>
              <span>TEXAS, UNITED STATES</span>
              <h3>
                Houston <ArrowUpRight />
              </h3>
              <p>Big horizons. A drive to match.</p>
            </div>
          </Link>
        </div>
      </section>
      <section className="supplier-banner">
        <div>
          <div className="eyebrow">FOR AMBITIOUS RENTAL PARTNERS</div>
          <h2>
            Your fleet deserves
            <br />
            an exceptional audience.
          </h2>
        </div>
        <div>
          <p>
            Bring your vehicles to a marketplace built around quality. Create
            your supplier profile and submit your first listing.
          </p>
          <Link className="button dark" href="/supplier">
            Become a partner <ArrowUpRight size={18} />
          </Link>
        </div>
      </section>
    </>
  );
}
