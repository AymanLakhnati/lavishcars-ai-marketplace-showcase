"use client";
import Link from "next/link";
import { ArrowUpRight, Users, Gauge, MapPin } from "lucide-react";
import { Listing, mediaUrl, price } from "@/lib/api";
export function CarArt({
  variant = "",
  hero = false,
}: {
  variant?: string;
  hero?: boolean;
}) {
  const suv = /suv|range|g-class|bentayga|cullinan|urus/i.test(variant);
  return (
    <svg
      className={hero ? "car-art hero-car" : "car-art"}
      viewBox="0 0 900 400"
      role="img"
      aria-label="Original illustrative luxury vehicle silhouette"
    >
      <defs>
        <linearGradient
          id={hero ? "heroBody" : "body"}
          x1="0"
          y1="0"
          x2=".3"
          y2="1"
        >
          <stop stopColor={hero ? "#e0d9cc" : "#c8c3b8"} />
          <stop offset=".42" stopColor="#8c8c84" />
          <stop offset=".58" stopColor="#414843" />
          <stop offset="1" stopColor="#19221f" />
        </linearGradient>
        <linearGradient id="glass">
          <stop stopColor="#101d1b" />
          <stop offset=".6" stopColor="#4a615b" />
          <stop offset="1" stopColor="#17221e" />
        </linearGradient>
        <radialGradient id="wheel">
          <stop stopColor="#bfc1b9" />
          <stop offset=".2" stopColor="#222a27" />
          <stop offset=".6" stopColor="#8a908a" />
          <stop offset=".65" stopColor="#1c211f" />
          <stop offset="1" stopColor="#080d0b" />
        </radialGradient>
      </defs>
      <ellipse cx="470" cy="325" rx="355" ry="25" fill="#000" opacity=".25" />
      <path
        d={
          suv
            ? "M95 282 112 211 245 190 296 111 612 111 690 178 801 202 833 280 809 309 124 309Z"
            : "M85 278 116 234 273 203 367 139 580 140 691 204 797 221 834 277 812 307 109 307Z"
        }
        fill={`url(#${hero ? "heroBody" : "body"})`}
        stroke="#b4b5a9"
        strokeWidth="2"
      />
      <path
        d={
          suv
            ? "M269 187 310 125 452 125 452 187Z M469 125 601 125 667 187 469 187Z"
            : "M298 201 376 151 452 151 452 201Z M468 151 574 152 657 202 468 202Z"
        }
        fill="url(#glass)"
        stroke="#a3aaa0"
        strokeWidth="2"
      />
      <path
        d="M116 236 283 222 681 222 794 238 M448 213 448 289 M670 216 688 285"
        fill="none"
        stroke="#ced0c1"
        opacity=".35"
        strokeWidth="2"
      />
      <path
        d="M109 246 186 242 178 254 105 260 M767 235 807 244 811 253 767 250"
        fill="#f2f0d4"
      />
      <path d="M111 277 162 277 162 289 108 289" fill="#0d1613" />
      <rect x="487" y="225" width="32" height="5" rx="2" fill="#a5b0a5" />
      {[240, 703].map((x) => (
        <g key={x}>
          <circle cx={x} cy="291" r="60" fill="#111714" />
          <circle cx={x} cy="291" r="47" fill="url(#wheel)" />
          {[0, 60, 120].map((a) => (
            <path
              key={a}
              d={`M${x - 34} 291H${x + 34}`}
              transform={`rotate(${a} ${x} 291)`}
              stroke="#b6bbb0"
              strokeWidth="4"
            />
          ))}
          <circle cx={x} cy="291" r="10" fill="#8e998c" />
        </g>
      ))}
    </svg>
  );
}
export function VehicleImage({ listing }: { listing: Listing }) {
  return listing.images?.length ? (
    <img
      className="vehicle-photo"
      src={mediaUrl(listing.images[0])}
      alt={`${listing.brand} ${listing.model}`}
    />
  ) : (
    <>
      <CarArt variant={`${listing.category} ${listing.model}`} />
      <span className="illustration">Concept illustration</span>
    </>
  );
}
export function VehicleCard({
  listing,
  reasons,
  period = "daily",
}: {
  listing: Listing;
  reasons?: string[];
  period?: "daily" | "weekly" | "monthly";
}) {
  return (
    <article className="vehicle-card">
      <Link href={`/fleet/${listing.slug}`} className="vehicle-visual">
        <span className="vehicle-tag">{listing.category}</span>
        <VehicleImage listing={listing} />
        <span className="round-arrow">
          <ArrowUpRight size={18} />
        </span>
      </Link>
      <div className="vehicle-content">
        <div className="eyebrow location">
          <MapPin size={12} />
          {listing.city} <span>· {listing.year}</span>
        </div>
        <Link href={`/fleet/${listing.slug}`}>
          <h3>
            {listing.brand} <span>{listing.model}</span>
          </h3>
        </Link>
        <div className="specs">
          <span>
            <Users size={14} />
            {listing.seats} seats
          </span>
          <span>
            <Gauge size={14} />
            {listing.transmission}
          </span>
        </div>
        {reasons && (
          <ul className="match-reasons">
            {reasons.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        )}
        <div className="card-bottom">
          <span>
            <strong>
              {price(listing[`${period}_price`], listing.currency)}
            </strong>
            <small>
              {" "}
              /{" "}
              {period === "daily"
                ? "day"
                : period === "weekly"
                  ? "week"
                  : "month"}
            </small>
          </span>
          <Link href={`/fleet/${listing.slug}`}>
            View car <ArrowUpRight size={14} />
          </Link>
        </div>
      </div>
    </article>
  );
}
