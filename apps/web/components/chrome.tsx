"use client";
import Link from "next/link";
import { useState } from "react";
import { ArrowUpRight, Menu, X, Sparkles } from "lucide-react";
export function Header() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <div className="demo-bar">
        INDEPENDENT CONCEPT <span>•</span> Synthetic demo fleet. Inquiries are
        not reservations.
      </div>
      <header className="header">
        <Link href="/" className="wordmark">
          LAVISH<span>CARS</span>
          <small>THE ART OF THE DRIVE</small>
        </Link>
        <button
          className="mobile-toggle"
          aria-label="Toggle navigation"
          aria-expanded={open}
          aria-controls="primary-navigation"
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
        <nav
          id="primary-navigation"
          className={open ? "open" : ""}
          onClick={() => setOpen(false)}
        >
          <Link href="/fleet">Discover the fleet</Link>
          <Link href="/concierge">
            <Sparkles size={15} /> AI concierge
          </Link>
          <Link href="/supplier">For suppliers</Link>
          <Link className="nav-cta" href="/fleet">
            Find your drive <ArrowUpRight size={16} />
          </Link>
        </nav>
      </header>
    </>
  );
}
export function Footer() {
  return (
    <footer>
      <div className="footer-top">
        <Link href="/" className="wordmark">
          LAVISH<span>CARS</span>
        </Link>
        <p>
          Exceptional cars.
          <br />
          Extraordinary possibilities.
        </p>
        <div>
          <Link href="/fleet">Explore the fleet</Link>
          <Link href="/concierge">Meet your concierge</Link>
          <Link href="/supplier">Supplier portal</Link>
          <Link href="/admin">Admin console</Link>
        </div>
      </div>
      <div className="footer-bottom">
        <span>© 2026 LavishCars concept. Unofficial demonstration.</span>
        <span>
          No payments. No confirmed bookings. Just a better beginning.
        </span>
      </div>
    </footer>
  );
}
