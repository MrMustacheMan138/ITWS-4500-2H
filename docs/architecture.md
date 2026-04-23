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
│  │  │        ├─ ingest.py
│  │  │        └─ sources.py
│  │  ├─ core/
│  │  ├─ integrations/
│  │  │  └─ llm/
│  │  ├─ services/
│  │  │  ├─ link_fetcher.py
│  │  │  └─ pdf_processor.py
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
├─ data/
├─ docs/
├─ docker-compose.yml
├─ docker-compose.dev.yml
├─ package.json
└─ README.md
```

### Current backend file layout

**Layer Responsibilities:**
* Routers (API layer): HTTP handling only (request parsing/validation)
* Services (application layer): use-case orchestration and ingestion helpers
* Domain (business layer): curriculum logic, comparison/scoring rules, RAG citation requirements (scaffolded)
* Data (persistence layer): database models + DB session management
* Integrations (infrastructure layer): external services such as LLM connectors

``` Plain Text
apps/api/
├─ main.py                         # FastAPI app initialization, CORS middleware, router registration, startup events
├─ database.py                     # SQLAlchemy async engine, session factory, Base declarative, get_db() dependency
├─ models.py                       # SQLAlchemy ORM models (includes persisted entities like users/comparisons)
├─ requirements.txt                # Python dependencies (fastapi, uvicorn, sqlalchemy, asyncpg, pydantic, etc.)
│
├─ api/
│  ├─ __init__.py                  # API package init
│  └─ v1/
│     ├─ __init__.py               # v1 API package init
│     ├─ deps.py                   # Shared dependencies for routers
│     └─ routers/                  # API endpoint handlers
│        ├─ __init__.py
│        ├─ auth.py                # Authentication endpoints: /login and /register
│        ├─ ingest.py              # Ingestion endpoint model/route scaffold
│        └─ sources.py             # Source-management route placeholder (currently empty)
│
├─ services/                       # Use-case helpers (link fetching, PDF processing)
├─ core/                           # Core utilities scaffold (currently empty)
├─ integrations/                   # External service integrations
│  └─ llm/                         # LLM integration scaffold
│
├─ Dockerfile                      # Production Docker build
├─ Dockerfile.dev                  # Development Docker build with hot reload
└─ .env                            # Environment variables (DATABASE_URL, POSTGRES_* configs)
```

**Key Functional Files:**

- **`main.py`**: Entry point for FastAPI application. Initializes FastAPI, configures CORS for frontend communication, creates database tables on startup, and registers currently active routers.

- **`database.py`**: Database configuration and connection management. Builds async PostgreSQL connection URL from environment variables, creates async SQLAlchemy engine, configures async session factory, defines Base class for ORM models, and provides `get_db()` dependency for route handlers.

- **`models.py`**: SQLAlchemy ORM model definitions used by the backend API and authentication logic.

- **`api/v1/routers/auth.py`**: Authentication endpoints. Defines request/response schemas and implements login + registration flows with password hashing and DB-backed user lookup.

- **`api/v1/routers/ingest.py`**: Data ingestion endpoint scaffold. Defines typed ingest payloads and response models for handling link/PDF entries.

- **`api/v1/routers/sources.py`**: Placeholder for data source management endpoints. File exists but currently contains no implementation.

- **Router mounting note**: `main.py` currently mounts the auth router at `/api/auth`; other router files exist but are not mounted yet.

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
│  │  │  ├─ login/page.tsx           # Business logic of login page
│  │  │  └─ signup/page.tsx          # Business logic of signup page
│  │  │
│  │  ├─ dashboard/
│  │  │  ├─ page.tsx                 # Dashboard home for user workflows
│  │  │  ├─ compare/new/page.tsx     # Start a new curriculum/program comparison
│  │  │  ├─ sources/page.tsx         # Source documents and status views
│  │  │  ├─ ingest/page.tsx          # Start ingestion flow
│  │  │  └─ results/page.tsx         # Comparison/output results view
│  │  ├─ api/
│  │  │  └─ auth/[...nextauth]/route.ts  # NextAuth handlers (frontend auth API route)
│  │  ├─ globals.css                 # Global styles for entire app (imported by layout.tsx)
│  │  ├─ layout.tsx                  # Root layout shell + provider wiring
│  │  ├─ page.tsx                    # Landing page (first page)
│  │  └─ providers.tsx               # SessionProvider + any global providers
│  │
│  ├─ components/                    # Technical components to import into business logic files
│  │  ├─ comparison/                 # Side-by-side views, compare forms, results views
│  │  ├─ chat/                       # AI assistant UI
│  │  ├─ auth/                       # Login/sign-up form components
│  │  └─ common/                     # Shared UI and layout components
│  │
│  ├─ lib/
│  │  ├─ api/
│  │  │  ├─ client.ts                # fetch wrapper (base URL, errors)
│  │  │  └─ endpoints.ts             # API calls for backend operations
│  │  ├─ auth/
│  │  │  ├─ session.ts               # server/client session helpers
│  │  │  └─ rbac.ts                  # role checks (admin/editor/viewer)
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

- **`src/auth.ts`**: NextAuth.js configuration. Defines credentials auth, connects to backend auth endpoints, validates credentials, and maps authenticated user/session data.

- **`src/app/layout.tsx`**: Root application layout. Wraps all pages with providers, defines HTML shell, and imports `src/app/globals.css` for global styling.

- **`src/app/providers.tsx`**: Global context providers. Wraps app with NextAuth SessionProvider to make authentication state available throughout the app.

- **`src/app/api/auth/[...nextauth]/route.ts`**: Next.js App Router API endpoint that exports GET/POST NextAuth handlers. This is the currently active `app/api` route.

- **`src/components/auth/LoginForm.tsx`**: Client-side login form component with validation, auth call, error handling, and redirect behavior.

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
