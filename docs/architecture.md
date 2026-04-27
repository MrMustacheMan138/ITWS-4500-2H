# Architecture Overview

This repository follows a layered architecture with a clear separation between:

Presentation (Next.js web UI)

Application logic (FastAPI routers + service scaffolds)

Business logic (domain scoring and curriculum rules)

Data access (SQLAlchemy models + PostgreSQL)

Integrations (PDF/URL parsing, chunking, embeddings, LLM hooks)

Infrastructure (Docker Compose, environment config, deployment)

The goal is to keep each layer focused on one responsibility so the codebase stays maintainable as the ingestion and comparison pipeline grows.

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
│  ├─ api/
│  │  ├─ main.py
│  │  ├─ database.py
│  │  ├─ models.py
│  │  ├─ requirements.txt
│  │  ├─ api/
│  │  │  └─ v1/
│  │  │     ├─ deps.py
│  │  │     └─ routers/
│  │  │        ├─ auth.py
│  │  │        ├─ comparisons.py
│  │  │        ├─ ingest.py
│  │  │        ├─ programs.py
│  │  │        └─ sources.py
│  │  ├─ core/
│  │  │  ├─ auth.py
│  │  │  └─ config.py
│  │  ├─ domain/
│  │  │  ├─ curriculum/
│  │  │  └─ scoring/
│  │  ├─ integrations/
│  │  │  ├─ embeddings/
│  │  │  ├─ llm/
│  │  │  └─ parsers/
│  │  ├─ services/
│  │  │  ├─ analysis.py
│  │  │  └─ ingestion.py
│  │  ├─ Dockerfile
│  │  └─ Dockerfile.dev
│  └─ web/
│     ├─ src/
│     │  ├─ app/
│     │  │  ├─ (auth)/
│     │  │  │  ├─ login/page.tsx
│     │  │  │  └─ signup/page.tsx
│     │  │  ├─ api/
│     │  │  │  └─ auth/[...nextauth]/route.ts
│     │  │  ├─ dashboard/
│     │  │  │  ├─ page.tsx
│     │  │  │  ├─ compare/new/page.tsx
│     │  │  │  ├─ ingest/page.tsx
│     │  │  │  ├─ results/page.tsx
│     │  │  │  └─ sources/page.tsx
│     │  │  ├─ globals.css
│     │  │  ├─ layout.tsx
│     │  │  ├─ page.tsx
│     │  │  └─ providers.tsx
│     │  ├─ auth.ts
│     │  ├─ components/
│     │  ├─ lib/
│     │  └─ types/
│     ├─ public/
│     ├─ next.config.js
│     ├─ package.json
│     ├─ tsconfig.json
│     ├─ Dockerfile
│     └─ Dockerfile.dev
├─ docs/
├─ docker-compose.yml
├─ docker-compose.dev.yml
├─ package.json
└─ README.md
```

### Current backend file layout

**Layer Responsibilities:**
* Routers (API layer): HTTP handling, validation, and response shaping
* Services (application layer): ingestion and analysis orchestration scaffolds
* Domain (business layer): curriculum section rules and rigor scoring
* Data (persistence layer): SQLAlchemy models and DB session management
* Integrations (infrastructure layer): PDF/URL parsing, chunking, embeddings, and LLM hooks

``` Plain Text
apps/api/
├─ main.py                         # FastAPI app initialization, CORS middleware, router registration, startup events
├─ database.py                     # SQLAlchemy async engine, session factory, Base declarative, get_db() dependency
├─ models.py                       # SQLAlchemy ORM models for users, programs, sources, and comparisons
├─ requirements.txt                # Python dependencies (fastapi, uvicorn, sqlalchemy, asyncpg, pydantic, etc.)
│
├─ api/
│  ├─ __init__.py                  # API package init
│  └─ v1/
│     ├─ __init__.py               # v1 API package init
│     ├─ deps.py                   # Shared dependencies for routers
│     └─ routers/                  # API endpoint handlers
│        ├─ __init__.py
│        ├─ auth.py                # Authentication endpoints for login and signup
│        ├─ comparisons.py         # Comparison CRUD endpoints
│        ├─ ingest.py              # Ingest request/response schema and queueing scaffold
│        ├─ programs.py            # Program CRUD endpoints
│        └─ sources.py             # Source CRUD endpoints and pending status creation
│
├─ core/                           # Auth and configuration helpers
├─ domain/                         # Curriculum section rules and rigor scoring
├─ integrations/                   # External parsing/chunking/embedding/LLM helpers
│  ├─ embeddings/
│  ├─ llm/
│  └─ parsers/
├─ services/                       # Ingestion and analysis orchestration scaffolds
│
├─ Dockerfile                      # Production Docker build
├─ Dockerfile.dev                  # Development Docker build with hot reload
└─ .env                            # Environment variables (DATABASE_URL, JWT, PostgreSQL config)
```

**Key Functional Files:**

- **`main.py`**: Entry point for the FastAPI application. Initializes FastAPI, configures CORS for the frontend, creates database tables on startup, and mounts the active v1 routers.

- **`database.py`**: Database configuration and connection management. Builds the async PostgreSQL connection from environment variables, creates the SQLAlchemy async engine, configures the session factory, defines `Base`, and provides `get_db()`.

- **`models.py`**: SQLAlchemy ORM model definitions for `User`, `Program`, `Source`, and `Comparison`.

- **`api/v1/routers/auth.py`**: Authentication endpoints. Implements login and signup with password hashing, DB-backed user lookup, and token creation.

- **`api/v1/routers/ingest.py`**: Ingest route scaffold. Accepts typed PDF/link entries and currently returns queued/success status messages.

- **`api/v1/routers/sources.py`**: Source management endpoints. Creates, lists, updates, and deletes source records for the current user.

- **`services/ingestion.py`**: Ingestion orchestration scaffold for parsing, chunking, embeddings, section analysis, and score persistence.

- **`services/analysis.py`**: Section analysis scaffold for LLM-based section scoring and JSON parsing.

- **`integrations/parsers/pdf_parser.py`**: PDF parsing helper that extracts table and text chunks from uploaded documents.

- **`integrations/parsers/link_parser.py`**: URL parsing helper that fetches a page and returns chunked readable text.

- **`integrations/parsers/document_parser.py`**: LLM parsing scaffold for turning raw text into structured curriculum sections.

- **`integrations/embeddings/chunker.py`**: Chunking and embedding scaffold used by the ingestion pipeline.

### Current frontend file layout

**Responsibilities:**
* UI rendering with React Server Components and Client Components
* API communication with backend FastAPI service
* Session-based authentication and route protection (NextAuth.js)
* Form validation and user interactions

``` Plain Text
apps/web/
├─ src/
│  ├─ app/
│  │  ├─ (auth)/
│  │  │  ├─ login/page.tsx           # Login page shell
│  │  │  └─ signup/page.tsx          # Signup page shell
│  │  │
│  │  ├─ dashboard/
│  │  │  ├─ page.tsx                 # Dashboard home for user workflows
│  │  │  ├─ compare/new/page.tsx     # Start a new curriculum/program comparison
│  │  │  ├─ sources/page.tsx         # Source documents and status views
│  │  │  ├─ ingest/page.tsx          # Start ingestion flow
│  │  │  └─ results/page.tsx         # Comparison/output results view
│  │  ├─ api/
│  │  │  └─ auth/[...nextauth]/route.ts  # NextAuth handlers (frontend auth API route)
│  │  ├─ globals.css                 # Global styles for entire app
│  │  ├─ layout.tsx                  # Root layout shell + provider wiring
│  │  ├─ page.tsx                    # Landing page
│  │  └─ providers.tsx               # SessionProvider and shared providers
│  │
│  ├─ components/                    # Shared UI components
│  │  ├─ comparison/
│  │  ├─ chat/
│  │  ├─ auth/
│  │  └─ common/
│  │
│  ├─ lib/
│  │  ├─ api/
│  │  │  ├─ client.ts                # fetch wrapper (base URL, errors)
│  │  │  └─ endpoints.ts             # API calls for backend operations
│  │  ├─ auth/
│  │  │  ├─ session.ts               # server/client session helpers
│  │  │  └─ rbac.ts                  # role checks
│  │  ├─ schema/                     # zod schemas for forms
│  │  └─ utils/
│  │
│  └─ types/
│
├─ public/
├─ next.config.js
├─ package.json
└─ tsconfig.json
```

**Key Functional Files:**

- **`src/auth.ts`**: NextAuth.js configuration. Defines credentials auth and forwards login requests to the backend `/api/v1/auth/login` endpoint.

- **`src/app/layout.tsx`**: Root application layout. Wraps all pages with providers and defines the HTML shell.

- **`src/app/providers.tsx`**: Global context providers. Wraps the app with `SessionProvider`.

- **`src/app/api/auth/[...nextauth]/route.ts`**: Next.js App Router API endpoint that exports GET/POST NextAuth handlers.

- **`src/components/auth/LoginForm.tsx`**: Client-side login form component with validation, NextAuth sign-in, error handling, and redirect behavior.

- **`src/components/auth/SignUpForm.tsx`**: Client-side signup form component with validation and registration workflow.

- **`src/lib/schema/auth.ts`**: Form validation schemas using Zod for login and signup payloads.

- **`src/lib/api/client.ts`**: API client wrapper with shared fetch configuration and error handling.

- **`src/lib/api/endpoints.ts`**: Type-safe API endpoint wrappers used by frontend flows.

- **`src/lib/auth/session.ts`**: Session management helpers for server/client session retrieval.

- **`src/lib/auth/rbac.ts`**: Role-based access control helpers for auth-aware UI and route behavior.

---

## Development Workflow

### Docker Compose Setup

The project uses Docker Compose with separate configurations for development and production:

- **`docker-compose.yml`**: Base configuration with service definitions
- **`docker-compose.dev.yml`**: Development overrides with volume mounts for hot reload

**Start development environment:**
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Rebuild after dependency changes:**
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Hot Reload

The development setup includes volume mounts that enable hot reloading:
- **Web (Next.js)**: Changes to `.tsx`/`.ts` files automatically reload
- **API (FastAPI)**: Uvicorn watches for `.py` file changes and auto-reloads
- **No rebuild needed** for code changes - only for dependency or Dockerfile changes
