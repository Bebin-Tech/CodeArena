# CodeArena on Vercel

The `codearena` project belongs to `bebin-dotms-projects` and is connected to `Bebin-Tech/CodeArena`, production branch `main`.

## Deployment architecture

The root `vercel.json` uses **Vercel Services (beta)** to deploy the Next.js frontend and Python 3.13 FastAPI backend together. `/api/v1/*`, `/docs` and `/openapi.json` route to FastAPI; other routes go to Next.js. Both services share a domain, so browser authentication remains same-origin. The local loopback rewrite is disabled on Vercel.

Functions and storage use Singapore (`sin1`). Node.js is set to 24. PostgreSQL uses a separate Neon free-plan resource named `codearena-postgres`; Redis uses `codearena-redis` on Upstash's free plan with paid automatic upgrades disabled. Credentials are supplied by Marketplace connections, not committed files. These production resources are separate from Docker development data.

## Environment

| Variable | Purpose |
| --- | --- |
| `ENVIRONMENT=production` | Secure cookies and production database connection handling |
| `SECRET_KEY` | New production-only signing secret stored in Vercel |
| `DATABASE_URL` | Neon pooled PostgreSQL URL, normalized to psycopg 3 |
| `DATABASE_URL_UNPOOLED` | Direct URL for migrations when available |
| `KV_URL` or `REDIS_URL` | Hosted TLS Redis URL |
| `VERCEL_PROJECT_PRODUCTION_URL` | Vercel's canonical domain; default origin and email link base |
| `FRONTEND_URL`, `API_URL` | Optional explicit HTTPS domain overrides, e.g. after attaching a custom domain |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_STARTTLS`, `SMTP_USERNAME` | Transactional email connection |
| `SMTP_PASSWORD` or `RESEND_API_KEY` | Email credential (server-only) |
| `MAIL_FROM` | Authenticated Gmail address, or a sender on a domain verified with another email provider |
| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` | Optional GitHub OAuth credentials |

Gmail works without buying a domain: use `smtp.gmail.com`, port `587`, STARTTLS, your Gmail address as username/From, and a Google App Password as `SMTP_PASSWORD`. Follow [Gmail setup](gmail-setup.md).

For Resend SMTP use host `smtp.resend.com`, port `587`, STARTTLS enabled, username `resend`, and the API key as password. Resend requires a verified sender domain. Until email settings are complete, the account pages report email as unavailable and disable actions that require delivery. Existing sessions and verification/recovery links remain checked by the backend; no verification bypass or public default account is introduced.

## Migrations

From a checkout linked to this exact Vercel project:

```powershell
npm.cmd exec --yes --package=vercel@66.2.0 -- vercel project inspect --non-interactive
npm.cmd exec --yes --package=vercel@66.2.0 -- vercel env run -e production -- .venv\Scripts\python.exe scripts\migrate-production.py
```

The migration helper refuses missing or loopback database URLs and uses the explicitly injected hosted URL. It never copies local users into production. Initial identity migrations were applied to the new Neon database during deployment setup.

## Verification and operation

- Run backend tests and the frontend tests/build before releasing changes. The deployment update passed **22 backend tests**, **3 frontend tests**, and the Vercel-mode production build locally.
- Check `/api/v1/health` for database and Redis connectivity and `/api/v1/auth/providers` for configured identity providers and email readiness.
- Registration and recovery require working SMTP credentials (Gmail App Password or another configured provider); live GitHub OAuth requires provider credentials.
- Git pushes to `main` may trigger Vercel production deployments. Schema changes must remain compatible with the running version; apply reviewed migrations before shipping dependent code.
- Preview deployments intentionally do not receive the production database, Redis, or signing secret. Provision separate preview resources before testing authenticated previews.
- Roll back the complete application using Vercel's previous known-good production deployment. Database rollback is a separate reviewed operation; do not automatically downgrade migrations.
- Enable provider backups/restore according to the chosen plan before relying on real user data. Centralized monitoring, load testing and full commercial-release hardening remain later milestone work.

References: [Vercel Services](https://vercel.com/docs/services), [request header guarantees](https://vercel.com/docs/headers/request-headers), [Resend SMTP](https://resend.com/changelog/smtp-service).
