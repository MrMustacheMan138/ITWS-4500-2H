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

### Current backend file layout

**Layer Responsibilities:**
* Routers (API layer): HTTP handling only (request parsing/validation)
* Services (application layer): use-case orchestration (TODO: implement)
* Domain (business layer): curriculum logic, comparison/scoring rules, RAG citation requirements (TODO: implement)
* Data (persistence layer): database models + repositories + migrations
* Integrations (infrastructure layer): object storage, fetching, parsing, embeddings

``` Plain Text
apps/api/
├─ main.py                         # FastAPI app initialization, CORS middleware,router registration, startup events
├─ database.py                     # SQLAlchemy async engine, session factory, Base declarative, get_db() dependency
├─ models.py                       # SQLAlchemy ORM models (Comparison table currently defined)
├─ requirements.txt                # Python dependencies (fastapi, uvicorn, sqlalchemy, asyncpg, pydantic, email-validator, etc.)
│
├─ api/
│  ├─ __init__.py                  # API package init
│  └─ v1/
│     ├─ __init__.py               # v1 API package init
│     ├─ deps.py                   # Shared dependencies: db session, auth checks (TODO: implement)
│     └─ routers/                  # API endpoint handlers
│        ├─ __init__.py
│        ├─ auth.py                # Authentication endpoints: /login (returns JWT token)
│        ├─ ingest.py              # Data ingestion endpoints: /ingest (accepts PDFs, links, images)
│        └─ sources.py             # Data source management endpoints (TODO: implement CRUD)
│
├─ services/                       # (Empty) Use cases: ingestion processing, comparison logic, AI services
├─ domain/                         # (Empty) Pure business rules: scoring, diff logic, parsing rules
├─ core/                           # (Empty) Core utilities: config, security, rate limiting
├─ integrations/                   # (Empty) External service integrations: storage, fetchers, parsers, embeddings
│
├─ Dockerfile                      # Production multi-stage Docker build
├─ Dockerfile.dev                  # Development Docker build with hot reload
└─ .env                            # Environment variables (DATABASE_URL, POSTGRES_* configs)
```

**Key Functional Files:**

- **`main.py`**: Entry point for FastAPI application. Initializes FastAPI with title/version, configures CORS for frontend communication (localhost:3000), includes routers with prefixes, and sets up database table creation on startup.

- **`database.py`**: Database configuration and connection management. Builds async PostgreSQL connection URL from environment variables, creates async SQLAlchemy engine, configures async session factory, defines Base class for ORM models, and provides `get_db()` dependency for route handlers.

- **`models.py`**: SQLAlchemy ORM model definitions. Currently includes `Comparison` model with id, title, and created_at fields. All models extend Base from database.py.

- **`api/v1/routers/auth.py`**: Authentication endpoints. Defines `LoginRequest` (email + password) and `LoginResponse` (access_token) Pydantic models. POST /login endpoint validates credentials (TODO: implement actual password hashing and DB verification) and returns JWT token.

- **`api/v1/routers/ingest.py`**: Data ingestion endpoints. Accepts JSON body with list of entries (type: pdf/link/image, content: URL or base64, metadata: optional). POST /ingest endpoint processes each entry based on type and returns detailed success/failure results.

- **`api/v1/deps.py`**: Dependency injection for routes. Will contain reusable dependencies like database session retrieval, current user authentication, and role-based access checks.

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
│  │  │  ├─ page.tsx                 # “my comparisons / ingestions”
│  │  │  ├─ sources/page.tsx          # uploaded docs + status
│  │  │  └─ ingest/page.tsx           # start ingestion flow
│  │  ├─ api/
│  │  │  └─ auth/[...nextauth]/route.ts
│  │  ├─ layout.tsx                  
│  │  ├─ page.tsx                    # Landing page (first page)
│  │  └─ providers.tsx               # SessionProvider + any global providers
│  │
│  ├─ components/                    # Technical components to import into business logic files
│  │  ├─ comparison/                 # side-by-side tables, diff highlighting
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

**Key Functional Files:**

- **`src/auth.ts`**: NextAuth.js configuration. Defines CredentialsProvider for email/password authentication, connects to FastAPI backend at `/api/v1/auth/login`, validates credentials with Zod schema, and handles user session data.

- **`src/app/layout.tsx`**: Root application layout. Wraps all pages with SessionProvider for authentication state, defines HTML structure, and loads global CSS.

- **`src/app/providers.tsx`**: Global context providers. Currently wraps app with NextAuth SessionProvider to make authentication state available throughout the app.

- **`src/components/auth/LoginForm.tsx`**: Client-side login form component. Uses Zod schema validation, manages form state with React hooks, calls NextAuth signIn() with credentials provider, displays validation errors, and redirects to dashboard on success.

- **`src/components/auth/SignUpForm.tsx`**: Client-side signup form component. Validates email, password, confirm password, and name fields. Handles registration API call and error display.

- **`src/lib/schema/auth.ts`**: Form validation schemas using Zod. Exports `loginSchema` (email + 8+ char password) and `signupSchema` (with name and password confirmation). Provides TypeScript types via `z.infer`.

- **`src/lib/api/client.ts`**: API client wrapper. Provides base fetch configuration with error handling, authentication headers, and base URL management for backend API calls.

- **`src/lib/api/endpoints.ts`**: Type-safe API endpoint functions. Exports async functions that wrap fetch calls to specific backend routes (e.g., `getPrograms()`, `compare()`).

- **`src/lib/auth/session.ts`**: Session management helpers. Provides utilities to get current session on server and client, check authentication status, and access user data.

- **`src/lib/auth/rbac.ts`**: Role-based access control. Functions to check user roles (admin/editor/viewer) and conditionally render UI or protect routes based on permissions.

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