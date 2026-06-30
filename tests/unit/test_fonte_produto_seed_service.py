import json
from decimal import Decimal

import pytest

from src.dto.cupom_dto import LojaCupom
from src.service.fonte_produto_seed_service import FonteProdutoSeedService


def test_carregar_fontes_de_produtos_de_json(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "fontes.json"
    caminho.write_text(
        json.dumps(
            [
                {
                    "loja": "amazon",
                    "categoria": "teclado",
                    "url": "https://www.amazon.com.br/s?k=teclado+mecanico",
                    "preco_minimo": "100",
                    "preco_maximo": "1000",
                    "palavras_obrigatorias": ["teclado", "mecanico"],
                    "palavras_bloqueadas": ["membrana"],
                    "marcas_prioritarias": ["redragon"],
                    "limite_por_marca": 2,
                }
            ]
        ),
        encoding="utf-8",
    )

    fontes = FonteProdutoSeedService().carregar_de_arquivo(caminho)

    assert len(fontes) == 1
    assert fontes[0].loja == LojaCupom.AMAZON
    assert fontes[0].categoria == "teclado"
    assert fontes[0].preco_minimo == Decimal("100")
    assert fontes[0].preco_maximo == Decimal("1000")
    assert fontes[0].palavras_obrigatorias == ["teclado", "mecanico"]
    assert fontes[0].palavras_bloqueadas == ["membrana"]
    assert fontes[0].marcas_prioritarias == ["redragon"]
    assert fontes[0].limite_por_marca == 2
    assert fontes[0].ignorar_patrocinados is True


def test_rejeita_json_de_fontes_que_nao_e_lista(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "fontes.json"
    caminho.write_text(json.dumps({"loja": "amazon"}), encoding="utf-8")

    with pytest.raises(ValueError, match="precisa conter uma lista"):
        FonteProdutoSeedService().carregar_de_arquivo(caminho)
