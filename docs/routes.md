# Routes

This project exposes two route surfaces:

- The FastAPI backend, mounted under `/api/v1`.
- The Next.js frontend pages, which provide the user-facing UI.

## Backend API Routes

### Public utility routes

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Simple API status response that confirms the backend is running. |
| `GET` | `/health` | Health check endpoint used for monitoring and deployment checks. |

### Authentication

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Authenticates a user with email and password, then returns a bearer access token plus basic user info. |
| `POST` | `/api/v1/auth/signup` | Creates a new user account and returns the created user record. |

### Ingestion

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/v1/ingest/` | Accepts uploaded files and/or URLs for a program, processes them, and runs program-level analysis. |

### Sources

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/v1/sources/` | Lists the current user's sources, optionally filtered by `program_id` or `status`. |
| `GET` | `/api/v1/sources/{source_id}` | Returns one source owned by the current user. |
| `POST` | `/api/v1/sources/` | Creates a source record for the current user. |
| `PUT` | `/api/v1/sources/{source_id}` | Updates an existing source owned by the current user. |
| `DELETE` | `/api/v1/sources/{source_id}` | Deletes a source owned by the current user. |

### Programs

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/v1/programs/` | Lists all programs created by the current user. |
| `POST` | `/api/v1/programs/` | Creates a new academic program record. |
| `GET` | `/api/v1/programs/{program_id}` | Returns one program owned by the current user. |
| `PUT` | `/api/v1/programs/{program_id}` | Updates a program owned by the current user. |
| `DELETE` | `/api/v1/programs/{program_id}` | Deletes a program owned by the current user. |
| `GET` | `/api/v1/programs/{program_id}/analysis` | Returns the stored analysis summary for a program. |

### Comparisons

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/v1/comparisons/` | Lists all comparisons owned by the current user. |
| `GET` | `/api/v1/comparisons/usage` | Returns the user's comparison quota usage and remaining capacity. |
| `POST` | `/api/v1/comparisons/` | Creates a comparison record, optionally linking two programs. |
| `GET` | `/api/v1/comparisons/{comparison_id}` | Returns one comparison owned by the current user. |
| `POST` | `/api/v1/comparisons/{comparison_id}/run` | Runs the comparison pipeline and stores the generated comparison result. |

### Chat

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/v1/chat/` | Sends a chat message to the curriculum assistant and returns the generated reply. |

### NextAuth handler

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/auth/[...nextauth]` | NextAuth handler for session, callback, and sign-in related auth flow endpoints. |
| `POST` | `/api/auth/[...nextauth]` | NextAuth handler for session, callback, and sign-in related auth flow endpoints. |

## Frontend Routes

| Path | Description |
| --- | --- |
| `/` | Landing page that introduces the product and links into the dashboard or comparison flow. |
| `/login` | Sign-in page for existing users. |
| `/signup` | Account creation page for new users. |
| `/dashboard` | Main dashboard with comparison stats and recent comparisons. |
| `/dashboard/chat` | Chat interface for asking questions about curriculum comparisons. |
| `/dashboard/compare/new` | Form for creating a new comparison between two programs. |
| `/dashboard/ingest` | Upload and link ingestion page for adding source material to a program. |
| `/dashboard/results` | Results page for viewing a completed comparison. |
| `/dashboard/sources` | Source management page for browsing, filtering, and deleting ingested sources. |

## Notes

- Most backend routes are protected and expect an authenticated bearer token in the `Authorization` header.
- The dashboard pages rely on the user being signed in and on the NextAuth session being available before loading protected data.
