# Architecture Overview

This repository follows a layered architecture with a clear separation between:

Presentation (Next.js web UI)

Business logic (FastAPI services + domain rules)

Data access (PostgreSQL / repositories + object storage integrations)

Infrastructure (Docker Compose, volumes, deployment configuration)

The goal is to keep each layer focused on one responsibility so the codebase stays maintainable as features grow (ingestion, comparisons, RAG, citations, auth, etc.).

## Current repo structure:
Current top-level folders:
* `apps/api` - API service / backend
* `apps/web` - web / frontend
* `docs/` - documentation
* `docker-compose.yml` - local orchestration
* `data/` - runtime data

``` Plain Text
ITWS-4500-2H/
├─ apps/
│  ├─ api/                # was backend/
│  └─ web/                # was frontend/
├─ packages/
│  └─ shared/             # shared types/constants/api client
├─ infra/
│  ├─ docker/             # optional dockerfiles/nginx etc.
│  └─ scripts/            # seed/backfill/maintenance scripts
├─ docs/                  # keep your docs here
├─ docker-compose.yml
├─ .env.example
├─ README.md
└─ .github/
```

### Targeted backend file layout

Functionality:
* Routers (API layer): HTTP handling only (request parsing/validation)
* Services (application layer): use-case orchestration
* Domain (business layer): curriculum logic, comparison/scoring rules, RAG citation requirements
* Data (persistence layer): database models + repositories + migrations
* Integrations (infrastructure layer): object storage, fetching, parsing, embeddings

``` Plain Text
apps/api/
├─ app/
│  ├─ main.py                      # FastAPI init + middleware + router include
│  ├─ api/
│  │  └─ v1/
│  │     ├─ routers/               # endpoints only (no business logic)
│  │     └─ deps.py                # dependencies: db session, auth checks
│  ├─ services/                    # use cases: ingestion, comparison, AI
│  ├─ domain/                      # pure rules: scoring, diff logic, parsing rules
│  ├─ data/
│  │  ├─ db.py                     # engine/session
│  │  ├─ models/                   # SQLAlchemy models
│  │  ├─ repositories/             # DB queries/transactions
│  │  └─ migrations/               # Alembic migrations
│  ├─ integrations/
│  │  ├─ storage/                  # MinIO/S3 client wrapper
│  │  ├─ fetchers/                 # URL download/snapshotting
│  │  ├─ parsers/                  # HTML/PDF parsing adapters
│  │  └─ embeddings/               # embedding client + pgvector utilities
│  ├─ core/
│  │  ├─ config.py                 # env settings
│  │  ├─ security.py               # token verification + RBAC
│  │  └─ rate_limit.py             # rate limiting logic (esp AI endpoints, will implement later if we have time)
│  └─ tests/
├─ Dockerfile
├─ pyproject.toml
└─ alembic.ini
```

### Targeted frontend file layout

Functions:
* UI rendering
* calling backend APIs
* showing citations/snippets clearly
* session-based route gating (NextAuth)

``` Plain Text
apps/web/
├─ src/
│  ├─ app/
│  │  ├─ (public)/
│  │  │  ├─ page.tsx                 # landing / search
│  │  │  ├─ programs/page.tsx
│  │  │  └─ compare/page.tsx
│  │  ├─ (auth)/
│  │  │  ├─ login/page.tsx
│  │  │  └─ onboarding/page.tsx
│  │  ├─ dashboard/
│  │  │  ├─ page.tsx                 # “my comparisons / ingestions”
│  │  │  ├─ sources/page.tsx          # uploaded docs + status
│  │  │  └─ ingest/page.tsx           # start ingestion flow
│  │  ├─ api/
│  │  │  └─ auth/[...nextauth]/route.ts
│  │  ├─ layout.tsx
│  │  └─ providers.tsx               # SessionProvider + any global providers
│  │
│  ├─ components/
│  │  ├─ comparison/                 # side-by-side tables, diff highlighting
│  │  ├─ citations/                  # citation drawer, snippet viewer
│  │  ├─ chat/                       # AI assistant UI
│  │  └─ common/                     # buttons, inputs, modals, etc. Common components
│  │
│  ├─ lib/
│  │  ├─ api/
│  │  │  ├─ client.ts                # fetch wrapper (base URL, errors)
│  │  │  └─ endpoints.ts             # functions like getPrograms(), compare()
│  │  ├─ auth/
│  │  │  ├─ session.ts               # server/client session helpers
│  │  │  └─ rbac.ts                  # role checks (admin/editor/viewer)
│  │  ├─ schema/                     # zod schemas for forms
│  │  └─ utils/
│  │
│  └─ styles/
│  
│
├─ public/
├─ middleware.ts                      # optional route gating if we have time
├─ next.config.js
├─ package.json
└─ tsconfig.json
```