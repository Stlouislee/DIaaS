"""
Unit tests for security module.
"""
import pytest
from fastapi import HTTPException

from app.core.security import get_current_user_id, KEY_PATTERN
from app.core.config import settings


pytestmark = pytest.mark.unit


class TestKeyPattern:
    """Tests for API key pattern validation."""
    
    def test_valid_key_matches(self):
        """Test that valid keys match the pattern."""
        valid_keys = [
            "12345678",
            "abcdefgh",
            "ABCDEFGH",
            "test-key-123",
            "test_key_456",
            "a" * 64  # max length
        ]
        
        for key in valid_keys:
            assert KEY_PATTERN.match(key), f"Key should be valid: {key}"
    
    def test_invalid_key_does_not_match(self):
        """Test that invalid keys don't match the pattern."""
        invalid_keys = [
            "1234567",  # too short
            "a" * 65,  # too long
            "key with spaces",
            "key@with#special",
            "",
            "key!",
        ]
        
        for key in invalid_keys:
            assert not KEY_PATTERN.match(key), f"Key should be invalid: {key}"


class TestGetCurrentUserId:
    """Tests for get_current_user_id function."""
    
    async def test_valid_key_returns_user_id(self):
        """Test that valid key returns the key as user ID."""
        api_key = "valid-test-key-123"
        result = await get_current_user_id(api_key)
        assert result == api_key
    
    async def test_invalid_format_raises_403(self):
        """Test that invalid key format raises 403."""
        invalid_key = "bad!"
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(invalid_key)
        
        assert exc_info.value.status_code == 403
        assert "Invalid API Key format" in exc_info.value.detail
    
    async def test_short_key_raises_403(self):
        """Test that too short key raises 403."""
        short_key = "1234567"  # 7 chars, need 8
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(short_key)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.parametrize("key", [
        "12345678",
        "test-key-abc",
        "TEST_KEY_XYZ",
        "a1b2c3d4e5f6",
    ])
    async def test_various_valid_keys(self, key):
        """Test various valid key formats."""
        result = await get_current_user_id(key)
        assert result == key
