import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routers import auth

# Build DATABASE_URL from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "database")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

os.environ["DATABASE_URL"] = (
   f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
   f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

app = FastAPI(title="Web Science API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:3000"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
   return {"message": "API is running"}

@app.get("/health")
async def health():
   return {"status": "healthy"}