from fastapi import APIRouter
from api.v1.routers import auth, ingest, sources

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])