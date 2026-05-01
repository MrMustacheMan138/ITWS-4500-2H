"""
Integration tests for /api/v1/comparisons and /api/v1/sources endpoints.
"""

import pytest

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def create_program(client, headers, name="Test Prog"):
    resp = await client.post("/api/v1/programs/", json={"name": name}, headers=headers)
    assert resp.status_code == 200
    return resp.json()["id"]


# ===========================================================================
# Comparisons
# ===========================================================================

class TestCreateComparison:
    async def test_create_comparison_success(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.post("/api/v1/comparisons/", json={"title": "MIT vs RPI"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "MIT vs RPI"
        assert "id" in data

    async def test_create_with_program_ids(self, client, db, user_and_token):
        _, headers = user_and_token
        prog_a = await create_program(client, headers, "Prog A")
        prog_b = await create_program(client, headers, "Prog B")
        resp = await client.post("/api/v1/comparisons/", json={
            "title": "A vs B",
            "program_a_id": prog_a,
            "program_b_id": prog_b,
        }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["program_a_id"] == prog_a

    async def test_create_comparison_without_auth_returns_401(self, client, db):
        resp = await client.post("/api/v1/comparisons/", json={"title": "Anon"})
        assert resp.status_code == 401

    async def test_comparison_results_initially_null(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.post("/api/v1/comparisons/", json={"title": "Fresh"}, headers=headers)
        assert resp.json()["comparison_results"] is None


class TestGetComparisons:
    async def test_get_comparisons_empty(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.get("/api/v1/comparisons/", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_comparisons_returns_own(self, client, db, user_and_token):
        _, headers = user_and_token
        await client.post("/api/v1/comparisons/", json={"title": "C1"}, headers=headers)
        await client.post("/api/v1/comparisons/", json={"title": "C2"}, headers=headers)
        resp = await client.get("/api/v1/comparisons/", headers=headers)
        titles = [c["title"] for c in resp.json()]
        assert "C1" in titles and "C2" in titles

    async def test_get_comparison_by_id(self, client, db, user_and_token):
        _, headers = user_and_token
        create_resp = await client.post("/api/v1/comparisons/", json={"title": "Specific"}, headers=headers)
        cid = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/comparisons/{cid}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Specific"

    async def test_get_nonexistent_comparison_returns_404(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.get("/api/v1/comparisons/99999", headers=headers)
        assert resp.status_code == 404

    async def test_get_other_users_comparison_returns_403(self, client, db, user_and_token):
        from models import User
        from core.auth import get_password_hash, create_access_token

        _, headers_a = user_and_token
        create_resp = await client.post("/api/v1/comparisons/", json={"title": "Private"}, headers=headers_a)
        cid = create_resp.json()["id"]

        user_b = User(email="cb@example.com", name="CB", hashed_password=get_password_hash("pass"))
        db.add(user_b)
        await db.commit()
        await db.refresh(user_b)
        headers_b = {"Authorization": f"Bearer {create_access_token({'sub': str(user_b.id)})}"}

        resp = await client.get(f"/api/v1/comparisons/{cid}", headers=headers_b)
        assert resp.status_code == 403


class TestComparisonUsage:
    async def test_usage_shows_correct_counts(self, client, db, user_and_token):
        _, headers = user_and_token
        await client.post("/api/v1/comparisons/", json={"title": "C1"}, headers=headers)
        await client.post("/api/v1/comparisons/", json={"title": "C2"}, headers=headers)
        resp = await client.get("/api/v1/comparisons/usage", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["used"] == 2
        assert "limit" in data
        assert data["remaining"] == data["limit"] - 2

    async def test_usage_without_auth_returns_401(self, client, db):
        resp = await client.get("/api/v1/comparisons/usage")
        assert resp.status_code == 401


class TestRunComparison:
    async def test_run_without_programs_returns_422(self, client, db, user_and_token):
        _, headers = user_and_token
        create_resp = await client.post("/api/v1/comparisons/", json={"title": "No Progs"}, headers=headers)
        cid = create_resp.json()["id"]
        resp = await client.post(f"/api/v1/comparisons/{cid}/run", headers=headers)
        assert resp.status_code == 422

    async def test_run_nonexistent_comparison_returns_404(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.post("/api/v1/comparisons/99999/run", headers=headers)
        assert resp.status_code == 404


# ===========================================================================
# Sources
# ===========================================================================

class TestCreateSource:
    async def test_create_source_success(self, client, db, user_and_token):
        user, headers = user_and_token
        prog_id = await create_program(client, headers)
        resp = await client.post("/api/v1/sources/", json={
            "program_id": prog_id,
            "source_type": "link",
            "source_url": "https://example.com/catalog",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["source_type"] == "link"
        assert data["status"] == "pending"

    async def test_create_source_without_auth_returns_401(self, client, db):
        resp = await client.post("/api/v1/sources/", json={
            "program_id": 1, "source_type": "link"
        })
        assert resp.status_code == 401


class TestGetSources:
    async def test_get_sources_empty(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.get("/api/v1/sources/", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_filter_by_program_id(self, client, db, user_and_token):
        _, headers = user_and_token
        prog_a = await create_program(client, headers, "A")
        prog_b = await create_program(client, headers, "B")
        await client.post("/api/v1/sources/", json={"program_id": prog_a, "source_type": "link"}, headers=headers)
        await client.post("/api/v1/sources/", json={"program_id": prog_b, "source_type": "link"}, headers=headers)

        resp = await client.get(f"/api/v1/sources/?program_id={prog_a}", headers=headers)
        assert resp.status_code == 200
        for src in resp.json():
            assert src["program_id"] == prog_a


class TestDeleteSource:
    async def test_delete_source_success(self, client, db, user_and_token):
        _, headers = user_and_token
        prog_id = await create_program(client, headers)
        create_resp = await client.post("/api/v1/sources/", json={
            "program_id": prog_id, "source_type": "link"
        }, headers=headers)
        src_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/v1/sources/{src_id}", headers=headers)
        assert resp.status_code == 204

    async def test_delete_nonexistent_source_returns_404(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.delete("/api/v1/sources/99999", headers=headers)
        assert resp.status_code == 404

    async def test_delete_other_users_source_returns_403(self, client, db, user_and_token):
        from models import User
        from core.auth import get_password_hash, create_access_token

        _, headers_a = user_and_token
        prog_id = await create_program(client, headers_a)
        create_resp = await client.post("/api/v1/sources/", json={
            "program_id": prog_id, "source_type": "link"
        }, headers=headers_a)
        src_id = create_resp.json()["id"]

        user_b = User(email="sb@example.com", name="SB", hashed_password=get_password_hash("pass"))
        db.add(user_b)
        await db.commit()
        await db.refresh(user_b)
        headers_b = {"Authorization": f"Bearer {create_access_token({'sub': str(user_b.id)})}"}

        resp = await client.delete(f"/api/v1/sources/{src_id}", headers=headers_b)
        assert resp.status_code == 403


# ===========================================================================
# Auth middleware edge cases
# ===========================================================================

class TestAuthMiddleware:
    async def test_expired_token_returns_401(self, client, db):
        from datetime import timedelta
        from core.auth import create_access_token

        token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
        resp = await client.get("/api/v1/programs/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    async def test_malformed_token_returns_401(self, client, db):
        resp = await client.get("/api/v1/programs/", headers={"Authorization": "Bearer garbage"})
        assert resp.status_code == 401

    async def test_missing_auth_header_returns_401(self, client, db):
        resp = await client.get("/api/v1/programs/")
        assert resp.status_code == 401