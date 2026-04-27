import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routers import auth, ingest, sources, programs, comparisons, chat
from database import init_db
import models
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
   await init_db()
   yield

app = FastAPI(title="Web Science API", version="1.0.0", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("=== 422 VALIDATION ERROR ===", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://web:3000",
        "http://0.0.0.0:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])
app.include_router(programs.router, prefix="/api/v1/programs", tags=["programs"])
app.include_router(comparisons.router, prefix="/api/v1/comparisons", tags=["comparisons"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}