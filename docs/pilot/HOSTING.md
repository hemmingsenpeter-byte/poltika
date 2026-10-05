# Hosting the pilot, password protected

How to put the pilot container online so testers can reach it, behind a
password. Nothing here is live until an operator (Pete) creates the hosting
account and sets the password; the repository holds no credentials.

## What the image does

- Serves the analyst page (`/analyst`), the population page
  (`/analyst/microsim`), and the API with its docs (`/docs`).
- **Refuses to start without a password.** Set `POLTIKA_ACCESS_PASSWORD`.
  Every page and route then asks for it (HTTP Basic authentication; the
  browser shows its own sign-in box). The username is `pilot`, or
  `POLTIKA_ACCESS_USER`. Only `/healthz` is open, for the platform's health
  check, and it returns nothing but `{"status": "ok"}`.
- Sends security headers on every response (a content security policy that
  forbids framing and other origins, `nosniff`, `no-referrer`, HSTS) and
  refuses request bodies over 64 KiB with 413 (`api/hardening.py`).
- Computes one population run at a time: a run takes tens of seconds of
  CPU, so a second run request while one is in progress gets 429 with
  `Retry-After` instead of queueing (`api/microsim.py`). There is no
  per-address rate limit; the password is what keeps strangers out, so
  a service run without one is open to anyone with the address.
- Listens on `$PORT` when the platform sets one, otherwise 8000.
- Includes the synthetic development population, generated from its
  committed spec at build time, so the population page works with no extra
  setup. Every population result carries the synthetic label.
- Runs without a database. Stored scenarios (`/scenarios`) then return 503;
  the calculation routes and both pages don't need one. To enable them, set
  `POLTIKA_DATABASE_URL` to a PostgreSQL database; the entrypoint applies
  the migrations at start.
- Reads `policy_specs/` from `/policy_specs`, the copy baked into the image
  at build time (`POLTIKA_POLICY_SPECS_DIR=/policy_specs`, set in the
  `Dockerfile`). To deploy a reviewed copy instead of the image's build-time
  snapshot -- e.g. a platform volume mount, a config-management step, or a
  sidecar that writes the directory before the container starts -- point
  `POLTIKA_POLICY_SPECS_DIR` at it. The variable is read once, when the
  process starts; the API then loads the policy files from that path for
  each calculation, so restart after changing the mount. Startup fails
  loudly if the WFF or Accommodation Supplement `policy.yaml` is missing
  there; the household and analyst routes also need `wff_as_interaction/`
  in the same directory, which startup does not check (ADR-0011,
  `tests/installed_artifact/test_installed_artifact.py`).

Basic authentication sends the password with every request, so only serve
it over HTTPS. The platforms below give every service an HTTPS address.

## Why not Vercel

Vercel runs serverless functions and front-end builds, not containers. The
pilot is one long-running FastAPI process in a Docker image, with its
policy files and population on disk. Running it on Vercel would mean
rebuilding it as serverless functions, which changes how it loads its
policy files and fits poorly with the in-memory population runs. A
container platform runs the image unchanged.

## Recommended: Render (web dashboard, no command line)

1. Create an account at render.com and connect GitHub, granting access to
   `hemmingsenpeter-byte/poltika`.
2. New → **Web Service** → pick the repository. Branch `main`. Render finds
   the `Dockerfile`; choose the Docker runtime if asked.
3. Environment variables:
   - `POLTIKA_ACCESS_PASSWORD`: a long random password (use a password
     manager). Mark it secret.
   - `POLTIKA_ACCESS_USER` (optional): the username, if not `pilot`.
4. Health check path: `/healthz`.
5. Create the service. The first build takes a few minutes. Open the
   `https://…onrender.com/analyst` address it gives, and sign in.

Render rebuilds on every push to `main` by default, so the hosted pilot
tracks merged work. Turn auto-deploy off to pin a version. Check Render's
current pricing: its free tier has been suspended when idle, which makes
the first request after a pause slow.

## Alternative: Fly.io (command line)

With `flyctl` installed and signed in, from the repository:

```sh
fly launch --no-deploy            # accept the Dockerfile; set internal port 8000
fly secrets set POLTIKA_ACCESS_PASSWORD='…'
fly deploy
```

Google Cloud Run and Railway also run the image unchanged; set the same
environment variable.

## Sharing it

- Give testers the address, the username and the password separately.
- Change the password by updating the environment variable; the platform
  restarts the service.
- Tell testers what the pilot is: a conditional simulation of Working for
  Families 2026-27 and the Accommodation Supplement from facts they assert,
  and a synthetic population that is not an estimate for New Zealand
  (`docs/pilot/GUIDE.md`, `docs/releases/`).
