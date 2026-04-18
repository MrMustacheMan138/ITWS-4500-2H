from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import api_router
from database import engine, Base
import models  # Import models so they're registered with Base

app = FastAPI(title="Web Science API", version="1.0.0")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CORS middleware for frontend communication
app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:3000"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
   return {"message": "API is running"}

@app.get("/health")
async def health():
   return {"status": "healthy"}