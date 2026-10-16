import type { Metadata } from "next";
import { IBM_Plex_Mono, Source_Sans_3, Source_Serif_4 } from "next/font/google";
import type { ReactNode } from "react";

import { AppShell } from "@/components/layout/AppShell";

import "@/styles/globals.css";

// Fetched and self-hosted at build time: the running app makes no external call.
// latin-ext carries the macronised vowels of te reo Māori.
const sans = Source_Sans_3({ subsets: ["latin", "latin-ext"], variable: "--font-source-sans", display: "swap" });
const serif = Source_Serif_4({
  subsets: ["latin", "latin-ext"],
  axes: ["opsz"],
  variable: "--font-source-serif",
  display: "swap",
});
const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: { default: "Poltika", template: "%s · Poltika" },
  description: "Deterministic New Zealand policy calculations on a synthetic population.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en-NZ" className={`${sans.variable} ${serif.variable} ${plexMono.variable}`}>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
