import type { Metadata } from "next";
import { IBM_Plex_Mono, Inter } from "next/font/google";
import type { ReactNode } from "react";

import { AppShell } from "@/components/layout/AppShell";

import "@/styles/globals.css";

// Fetched and self-hosted at build time: the running app makes no external call.
const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
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
    <html lang="en-NZ" className={`${inter.variable} ${plexMono.variable}`}>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
