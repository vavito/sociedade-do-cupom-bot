import hashlib
import hmac
from collections.abc import Mapping
from typing import Any


def gerar_assinatura(app_secret: str, params: Mapping[str, Any]) -> str:
    valores = []
    for chave in sorted(params):
        if chave in {"sign", "access_token"}:
            continue
        valor = params[chave]
        if valor is None:
            continue
        valores.append(f"{chave}{valor}")

    mensagem = "".join(valores).encode("utf-8")
    segredo = app_secret.encode("utf-8")
    return hmac.new(segredo, mensagem, hashlib.sha256).hexdigest().upper()
