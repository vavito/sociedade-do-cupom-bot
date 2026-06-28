import hashlib

from src.external.shopee.shopee_signature import gerar_authorization_header


def test_gerar_authorization_header() -> None:
    header = gerar_authorization_header("123", 1700000000, '{"query":"x"}', "secret")
    expected_signature = hashlib.sha256(b'1231700000000{"query":"x"}secret').hexdigest()

    assert header == (
        f"SHA256 Credential=123, Timestamp=1700000000, Signature={expected_signature}"
    )
