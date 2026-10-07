import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const WEB_DIR = resolve(__dirname, "../..");

// Load the real development config in a fresh process, then use Next's own
// path and header matchers. This covers the API/UI collision without mocking
// the matching rules or running a second development server in CI.
const probe = `
  import config from './next.config.mjs';
  import { createRequire } from 'node:module';
  const require = createRequire(import.meta.url);
  const { getPathMatch } = require('next/dist/shared/lib/router/utils/path-match');
  const { matchHas } = require('next/dist/shared/lib/router/utils/prepare-destination');
  const rewrites = config.rewrites ? await config.rewrites() : undefined;
  const routes = rewrites?.beforeFiles ?? [];
  const requests = [
    ['/analyst/examples', 'application/json'],
    ['/analyst', 'text/html'],
    ['/openapi.json', '*/*'],
    ['/household/calculate', '*/*'],
    ['/household/intake', '*/*'],
    ['/microsim/population', '*/*'],
    ['/scenarios', 'application/json'],
    ['/scenarios/abc', '*/*'],
    ['/scenarios', 'text/html,application/xhtml+xml,*/*;q=0.8'],
    ['/scenarios', '*/*', '1'],
    ['/scenarios/abc', 'application/json', '1'],
  ];
  const matches = requests.map(([path, accept, rsc]) => {
    const headers = { accept, ...(rsc ? { rsc } : {}) };
    const route = routes.find(route =>
      getPathMatch(route.source)(path) &&
      matchHas({ headers }, {}, route.has ?? [], route.missing ?? [])
    );
    return { path, accept, rsc, source: route?.source ?? null };
  });
  console.log(JSON.stringify({ hasRewrites: !!config.rewrites, matches }));
`;

type Probe = {
  hasRewrites: boolean;
  matches: { path: string; accept: string; rsc?: string; source: string | null }[];
};

function readConfig(mode: "development" | "production"): Probe {
  return JSON.parse(
    execFileSync(process.execPath, ["--input-type=module", "-e", probe], {
      cwd: WEB_DIR,
      env: { ...process.env, NODE_ENV: mode },
      encoding: "utf8",
    }),
  ) as Probe;
}

describe("development API proxy", () => {
  const config = readConfig("development");

  it("forwards household examples and the classic calculators' API requests", () => {
    expect(config.matches.slice(0, 6).map((request) => request.source)).toEqual([
      "/analyst/:path*",
      "/analyst/:path*",
      "/openapi.json",
      "/household/:path*",
      "/household/:path*",
      "/microsim/:path*",
    ]);
  });

  it("forwards JSON scenario requests before the colliding UI page", () => {
    expect(config.matches.slice(6, 8).map((request) => request.source)).toEqual([
      "/scenarios/:path*",
      "/scenarios/:path*",
    ]);
  });

  it("keeps browser HTML and Next RSC requests on the frontend", () => {
    expect(config.matches.slice(8).map((request) => request.source)).toEqual([null, null, null]);
  });

  it("omits all rewrites from the production static export", () => {
    expect(readConfig("production").hasRewrites).toBe(false);
  });
});
