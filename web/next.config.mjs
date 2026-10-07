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
          return {
            // The household API shares /scenarios with a UI page. Check its
            // JSON requests before page files, while keeping HTML and Next's
            // RSC navigation requests on the frontend.
            beforeFiles: [
              {
                source: "/scenarios/:path*",
                destination: `${API_ORIGIN}/scenarios/:path*`,
                has: [{ type: "header", key: "accept", value: "(?:application/json|\\*/\\*)" }],
                missing: [{ type: "header", key: "rsc" }],
              },
              { source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` },
              { source: "/workbench/:path*", destination: `${API_ORIGIN}/workbench/:path*` },
              { source: "/healthz", destination: `${API_ORIGIN}/healthz` },
              { source: "/analyst/:path*", destination: `${API_ORIGIN}/analyst/:path*` },
              { source: "/openapi.json", destination: `${API_ORIGIN}/openapi.json` },
              { source: "/household/:path*", destination: `${API_ORIGIN}/household/:path*` },
              { source: "/microsim/:path*", destination: `${API_ORIGIN}/microsim/:path*` },
            ],
            afterFiles: [],
            fallback: [],
          };
        },
      }
    : {}),
};

export default nextConfig;
