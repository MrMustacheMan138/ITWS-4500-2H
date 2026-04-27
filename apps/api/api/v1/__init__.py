from fastapi import APIRouter
from api.v1.routers import auth, chat, comparisons, ingest, programs, sources

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
api_router.include_router(comparisons.router, prefix="/comparisons", tags=["comparisons"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(chat.router)
