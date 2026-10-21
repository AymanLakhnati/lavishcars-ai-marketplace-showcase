import type { Metadata } from "next";
import "./globals.css";
import { Header, Footer } from "@/components/chrome";
export const metadata: Metadata = {
  title: "LavishCars — Every journey, exceptional.",
  description:
    "An independent marketplace concept. Discover luxury vehicles, connect with suppliers, and find your perfect drive.",
  robots: { index: false, follow: false },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main-content">
          Skip to content
        </a>
        <Header />
        <main id="main-content">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
