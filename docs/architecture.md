# CodeArena architecture and delivery plan

## Milestone 1 boundary

Ship a running Next.js App Router interface, design tokens, FastAPI authentication API, PostgreSQL migrations, Redis rate limits, audit records, and tested account workflows. OAuth is configurable through GitHub; real delivery uses SMTP. Local development uses Mailpit to inspect verification and recovery messages. Product modules after authentication remain explicitly planned rather than populated with fabricated data.

## System boundaries

Browser → Next.js same-origin `/api/v1` rewrite → FastAPI → PostgreSQL (authoritative records). Redis holds expiring rate-limit counters. SMTP handles transactional mail. HTTP-only signed JWT cookies reference revocable database sessions. Cookie mutations require an allowed Origin. Session renewal rotates the session identifier; logout and recovery revoke sessions. Passwords use Argon2. One-time email tokens are stored only as SHA-256 digests, expire, and are consumed under a database row lock.

FastAPI owns authorization. Public registration permits only student, developer, or candidate, never an administrator. Current roles are loaded from PostgreSQL on every request. Organization creation, membership and scoped repositories land in Milestone 2; tenant resources will require membership plus explicit permissions on every lookup. OAuth identities are bound by provider subject; existing email accounts cannot be silently linked.

API contracts live at `/docs` and `/openapi.json`; all product routes are versioned under `/api/v1`. SQLAlchemy owns persistence and Alembic owns schema changes. Migration application is explicit, not a side effect of API startup. API errors return useful status codes, forms expose accessible validation and pending states, and private responses disable caching.

## Repository map

| Directory | Responsibility |
| --- | --- |
| frontend/app | App Router pages and global tokens |
| frontend/components | Shared accessible interface primitives |
| frontend/features | Account forms and workspace features |
| frontend/lib, services, types, hooks | Validation, API transport, contracts, hooks |
| backend/app/api | Versioned request handlers and authorization dependencies |
| backend/app/core | Configuration, database, security |
| backend/app/models, schemas | Persistence entities and request contracts |
| backend/app/services, repositories | Mail/auth services and data access |
| backend/migrations, tests | Versioned schema and automated boundary tests |
| execution-engine | Future independent worker and hardened sandbox adapters |
| infrastructure | Local containers and later deployment/observability |
| scripts | Windows setup, startup and checks |

## Execution architecture (Milestones 3–4)

Submission API validates size/language and persists a job transactionally. A separate dispatcher feeds Redis; independent workers claim idempotent jobs and invoke a hardened sandbox service. The primary API never evaluates user code and never receives a Docker socket. Workers impose CPU/memory/process/time/output caps and per-job network/filesystem isolation. Hidden cases remain server-side. Sandbox evaluation and escape-resistance tests gate execution availability; plain Docker alone is insufficient for hostile workloads.

## Delivery milestones

1. Architecture, design system, account authentication, session/recovery/onboarding, migrations and tests.
2. Organizations, tenant isolation, permission catalog, user management and database-backed developer metrics.
3. Problem library, Monaco studio, independent hardened execution infrastructure.
4. Test-case verdicts, idempotent submission processing and execution analytics.
5. Competition lifecycle, transactional scoring, registrations and live leaderboards.
6. OpenAI/Ollama provider abstraction, contest policies, quotas and collaboration.
7. Private company assessments, hiring pipeline and college administration.
8. Subscription provider/webhooks, invoices, platform administration and audit tooling.
9. Security boundary review, load tests, backups/restore, production rollout and rollback.

Each milestone requires meaningful automated tests plus a running workflow check. Deployment, billing, AI providers and production OAuth/SMTP require environment-specific credentials. No Kubernetes rollout before local workflows pass.

## Authentication acceptance checks

Registration validation and role escalation prevention; Argon2 persistence; verification and recovery token expiry/replay; login verification gates; enumeration-resistant recovery; JWT signature/expiry plus database session revocation; CSRF Origin checks; rate limits shared through Redis; suspension; own-session access; password reset revokes all sessions; onboarding persistence; real PostgreSQL migrations; frontend production build; browser registration-to-workspace flow.
