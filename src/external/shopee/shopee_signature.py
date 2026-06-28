import hashlib


def gerar_authorization_header(app_id: str, timestamp: int, payload: str, secret: str) -> str:
    base = f"{app_id}{timestamp}{payload}{secret}"
    signature = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}"
