/** @type {import('next').NextConfig} */
const isDev = process.env.NODE_ENV === "development";
const API_ORIGIN = process.env.POLTIKA_API_ORIGIN ?? "http://localhost:8000";

const nextConfig = {
  // ADR-0023: a static export that FastAPI serves from the same image.
  output: "export",
  trailingSlash: false,
  images: { unoptimized: true },
  reactStrictMode: true,
  // Static export forbids rewrites at build time, so the development proxy to
  // the FastAPI process exists only under `next dev`.
  ...(isDev
    ? {
        async rewrites() {
          return [
            { source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` },
            { source: "/workbench/:path*", destination: `${API_ORIGIN}/workbench/:path*` },
            { source: "/healthz", destination: `${API_ORIGIN}/healthz` },
          ];
        },
      }
    : {}),
};

export default nextConfig;
