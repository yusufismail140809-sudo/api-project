from security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


def test_hash_password_hasilkan_string():
    """Hash password harus menghasilkan string panjang."""
    hashed = hash_password("rahasia123")
    assert isinstance(hashed, str)
    assert len(hashed) > 50
    assert hashed != "rahasia123"


def test_verify_password_benar():
    """Verify password benar harus return True."""
    hashed = hash_password("rahasia123")
    assert verify_password("rahasia123", hashed) is True


def test_verify_password_salah():
    """Verify password salah harus return False."""
    hashed = hash_password("rahasia123")
    assert verify_password("salah456", hashed) is False


def test_hash_berbeda_tiap_kali():
    """Hash yang sama input harus beda output (karena salt)."""
    hash1 = hash_password("rahasia123")
    hash2 = hash_password("rahasia123")
    assert hash1 != hash2


def test_create_and_decode_token():
    """Bikin token lalu decode balik — payload harus sama."""
    token = create_access_token({"sub": "1", "role": "user"})
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["role"] == "user"
    assert "exp" in payload


def test_decode_token_invalid():
    """Token palsu harus return None."""
    assert decode_token("token-palsu-123") is None
    assert decode_token("") is None