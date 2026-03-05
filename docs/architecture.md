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