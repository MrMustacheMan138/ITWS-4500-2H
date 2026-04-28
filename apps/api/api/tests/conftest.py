"""
Shared pytest fixtures for unit and integration tests.

The integration tests use an in-memory SQLite database so they can run
without a real Postgres / pgvector instance.  AI calls (Groq, Gemini) are
always patched out so the suite is fast and free.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# In-memory SQLite engine (replaces Postgres for tests)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Patch init_db so the FastAPI lifespan doesn't try to CREATE EXTENSION vector
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def patch_init_db():
    """Replace init_db with a SQLite-compatible table creator."""
    async def _sqlite_init_db():
        from database import Base
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    with patch("database.init_db", side_effect=_sqlite_init_db):
        yield


# ---------------------------------------------------------------------------
# Wire the FastAPI app to use the test DB
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def override_app_db():
    from main import app
    from database import get_db
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Per-test DB session (creates + tears down tables each test for isolation)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def db():
    from database import Base
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def client():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Convenience: create a user and return auth headers
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def user_and_token(db):
    from models import User
    from core.auth import get_password_hash, create_access_token

    user = User(
        email="testuser@example.com",
        name="Test User",
        hashed_password=get_password_hash("Password123"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


# ---------------------------------------------------------------------------
# Patch AI clients globally so no real network calls are made
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_ai():
    """Stub every external AI call so tests don't hit live APIs."""
    groq_response = MagicMock()
    groq_response.choices = [MagicMock(message=MagicMock(content='{"score_a": 70, "score_b": 65, "verdict": "A wins", "section_scores": [], "gaps": []}'))]

    gemini_response = MagicMock()
    gemini_response.text = '{"course_schedule": "Mon/Wed lectures", "core_requirements": "Calculus I"}'

    with (
        patch("groq.Groq") as mock_groq_cls,
        patch("google.genai.Client") as mock_genai_cls,
        patch("integrations.ai.client.client") as mock_ai_client,
    ):
        mock_groq_cls.return_value.chat.completions.create.return_value = groq_response
        mock_genai_cls.return_value.models.generate_content.return_value = gemini_response
        mock_ai_client.models.generate_content = AsyncMock(return_value=gemini_response)
        mock_ai_client.models.generate_content.return_value = gemini_response
        yield