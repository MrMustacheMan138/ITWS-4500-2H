"""
Unit tests for core/auth.py

Tests password hashing, token creation, and token verification without
touching the database or any network service.
"""

import pytest
from datetime import timedelta
from jose import jwt

from core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = get_password_hash("mysecretpassword")
        assert hashed != "mysecretpassword"

    def test_hash_is_bcrypt(self):
        hashed = get_password_hash("mysecretpassword")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_verify_correct_password(self):
        hashed = get_password_hash("correct_password")
        assert verify_password("correct_password", hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes_for_same_password(self):
        """bcrypt uses a random salt each time."""
        h1 = get_password_hash("same_password")
        h2 = get_password_hash("same_password")
        assert h1 != h2

    def test_empty_password_hashes(self):
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True

    def test_special_characters_in_password(self):
        pw = "P@$$w0rd!#%^&*()"
        hashed = get_password_hash(pw)
        assert verify_password(pw, hashed) is True


# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------

class TestCreateAccessToken:
    def test_returns_string(self):
        token = create_access_token({"sub": "42"})
        assert isinstance(token, str)

    def test_token_contains_sub_claim(self):
        token = create_access_token({"sub": "99"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "99"

    def test_token_contains_exp_claim(self):
        token = create_access_token({"sub": "1"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_custom_expiry_is_respected(self):
        from datetime import datetime, timezone
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(hours=2))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = exp - now
        # Should be ~2 hours (allowing 5s slack)
        assert timedelta(hours=1, minutes=59) < delta < timedelta(hours=2, seconds=5)

    def test_default_expiry_is_access_token_expire_minutes(self):
        from datetime import datetime, timezone
        token = create_access_token({"sub": "1"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = exp - now
        expected = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        assert abs(delta - expected) < timedelta(seconds=5)

    def test_additional_claims_preserved(self):
        token = create_access_token({"sub": "1", "role": "admin", "email": "a@b.com"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["role"] == "admin"
        assert payload["email"] == "a@b.com"


# ---------------------------------------------------------------------------
# Token verification
# ---------------------------------------------------------------------------

class TestVerifyToken:
    def test_valid_token_returns_payload(self):
        token = create_access_token({"sub": "7"})
        result = verify_token(token)
        assert result is not None
        assert result["sub"] == "7"

    def test_invalid_token_returns_none(self):
        assert verify_token("not.a.real.token") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token({"sub": "1"})
        tampered = token[:-4] + "XXXX"
        assert verify_token(tampered) is None

    def test_expired_token_returns_none(self):
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
        assert verify_token(token) is None

    def test_empty_string_returns_none(self):
        assert verify_token("") is None