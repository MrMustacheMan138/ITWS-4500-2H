import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routers import auth, ingest, sources
from database import engine, Base
import models  # Import models so they're registered with Base


# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
   async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
   yield # app runs here
   # teardown here

app = FastAPI(title="Web Science API", version="1.0.0", lifespan=lifespan)

# CORS middleware for frontend communication
app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:3000"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(ingest.router, prefix="api/v1/ingest", tags=["ingest"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])

@app.get("/")
async def root():
   return {"message": "API is running"}

@app.get("/health")
async def health():
   return {"status": "healthy"}