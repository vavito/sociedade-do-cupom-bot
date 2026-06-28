from src.external.aliexpress.aliexpress_signature import gerar_assinatura


def test_gerar_assinatura_ordena_parametros_e_ignora_sign() -> None:
    params = {
        "method": "aliexpress.affiliate.hotproduct.query",
        "app_key": "app-key",
        "timestamp": "2026-06-27 12:00:00",
        "sign": "valor-antigo",
    }

    assinatura = gerar_assinatura("secret", params)

    assert assinatura == "BA3AE3C30E02CC4DBEF18260579660B55313C798205CFF5B42E4DE0CE9E10077"
