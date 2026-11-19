# CodeArena

Compete. Code. Prove Your Skills.

Milestone 1 implements the account foundation: a Next.js App Router interface, FastAPI authentication, PostgreSQL migrations, Redis rate limits, local transactional email, profile onboarding and session management. See [architecture and milestones](docs/architecture.md), [design system](docs/design-system.md), and [verification results](docs/milestone-1.md).

Vercel hosting configuration and production setup are documented in [the deployment guide](docs/deployment-vercel.md). Hosted accounts use a separate database; the local QA account does not automatically exist online.

## Run the application

After the development environment below is initialized, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\init-app.ps1
```

Start each application in a separate PowerShell terminal at the repository root:

```powershell
# Terminal 1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-backend.ps1
```

```powershell
# Terminal 2
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-frontend.ps1
```

- Application: [http://127.0.0.1:3000](http://127.0.0.1:3000)
- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Development email inbox: [http://127.0.0.1:8025](http://127.0.0.1:8025)

Register with your own details, open the verification email in Mailpit, verify, and sign in. No default accounts or passwords are created. Use `127.0.0.1` consistently: cookie Origin validation expects `FRONTEND_URL`, which defaults to that hostname. Mailpit captures local mail and does not deliver messages to real recipients.

Initialization preserves existing secrets, generates `SECRET_KEY` if missing, installs locked dependencies, starts infrastructure and applies migrations. Never commit `.env` or expose signing keys through `NEXT_PUBLIC_` variables. For a frontend on another port/hostname, update `FRONTEND_URL`; for a remote backend, set the frontend's server-only `API_URL` environment variable before starting/building Next.js.

## Verify

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m pytest -q
Pop-Location
Push-Location frontend
npm.cmd test
npm.cmd run build
Pop-Location
.\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini check
# Requires both servers and Mailpit running; creates a unique local QA account:
.\.venv\Scripts\python.exe scripts\smoke-app.py
```

Backend tests migrate a random temporary PostgreSQL schema and roll back per test. They do not delete application records. The full-stack smoke script uses the Next.js HTTP proxy and real SMTP, PostgreSQL and Redis. It leaves a uniquely named QA account and audit records in the local database.

## External authentication and email

GitHub OAuth is implemented but hidden as an action until `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are configured. Register a GitHub OAuth application with callback `http://127.0.0.1:8000/api/v1/auth/github/callback`, set credentials in `.env`, and restart the backend. OAuth tests cover provider identity handling with a mocked provider and reject automatic linking to an existing email/password account. A real GitHub round trip requires your credentials and has not been verified.

For real transactional delivery configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_STARTTLS=true` and `MAIL_FROM`. Production requires HTTPS, `ENVIRONMENT=production`, managed secrets, a trusted proxy configuration and an external SMTP service. Mailpit and the local containers are development infrastructure. Durable mail outbox/retries and operational deployment hardening are pending later milestones.

## Development environment

| Tool | Purpose | Local setup |
| --- | --- | --- |
| VS Code | Development | Existing installation; recommended extensions in `.vscode` |
| Python 3.13 | FastAPI backend | Project virtual environment in `.venv` |
| Node.js 24 LTS + npm | Next.js frontend | Existing Node 24 installation; `.nvmrc` records major version |
| PostgreSQL 17 | Main database | Docker Compose, localhost:5432 |
| Redis 7.4 | Queue and caching | Docker Compose, localhost:6379 |
| Docker Desktop | Linux container infrastructure | WSL 2 backend |
| Git | Version control | Existing installation |

## Initialize

Start Docker Desktop and select Linux containers. If Docker requests WSL configuration or a restart, complete that in Windows first. See [Docker Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/).

Install missing tools with Windows Package Manager (skip tools already installed):

```powershell
winget install --id Python.Python.3.13 --exact --source winget
winget install --id OpenJS.NodeJS.LTS --exact --source winget
winget install --id Microsoft.VisualStudioCode --exact --source winget
winget install --id Git.Git --exact --source winget
winget install --id Docker.DockerDesktop --exact --source winget
```

The Node LTS installer tracks the current LTS. This workspace uses Node 24, an existing supported LTS installation; preserve that major for consistent development. See [Node release lifecycle](https://nodejs.org/en/about/previous-releases).

In a new PowerShell terminal at the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-dev.ps1 -StartServices
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev.ps1
```

`Bypass` applies only to the child process. Setup preserves existing `.env`, generates a local database password when needed, creates `.venv`, installs backend development dependencies and starts the database services. No global Python packages are installed.

`requirements-dev.txt` defines dependency ranges; `requirements-dev.lock.txt` records the exact installed Windows/Python 3.13 environment and is used by setup for repeatable installs.

Use the environment without activation:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip list
node --version
npm.cmd --version
docker compose ps
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
docker compose exec redis redis-cli ping
```

If `.cmd` launchers are restricted in your terminal, npm can also be invoked with `node 'C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js' --version`.

For future backend configuration use host `127.0.0.1`, database/user/port/password from `.env`, and Redis URL `redis://127.0.0.1:6379/0`. Containers on the Compose network use service names `postgres` and `redis` instead. Never expose the database password through a frontend environment variable.

Stop services with `docker compose stop`; restart with `docker compose up -d --wait`. Data persists in named Docker volumes. Changing `.env` credentials does not change an existing PostgreSQL volume's credentials; use SQL to rotate them.

These services are local development dependencies with ports bound to loopback. Redis is intended for this trusted local environment. Arbitrary code execution needs a separate hardened worker architecture before it can be enabled.

PostgreSQL and Redis CLIs are available inside the containers; host installations are unnecessary. See [Redis on Windows](https://redis.io/docs/latest/install/).
