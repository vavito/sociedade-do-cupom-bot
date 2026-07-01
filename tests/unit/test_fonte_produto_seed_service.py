import json
from decimal import Decimal
from pathlib import Path

import pytest

from src.dto.cupom_dto import LojaCupom
from src.service.fonte_produto_seed_service import FonteProdutoSeedService
from src.service.nicho_produto_service import NichoProduto


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
                    "exigir_marca_prioritaria": True,
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
    assert fontes[0].exigir_marca_prioritaria is True
    assert fontes[0].limite_por_marca == 2
    assert fontes[0].ignorar_patrocinados is True


def test_rejeita_json_de_fontes_que_nao_e_lista(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "fontes.json"
    caminho.write_text(json.dumps({"loja": "amazon"}), encoding="utf-8")

    with pytest.raises(ValueError, match="precisa conter uma lista"):
        FonteProdutoSeedService().carregar_de_arquivo(caminho)


def test_exemplo_de_fontes_cobre_nichos_focados() -> None:
    fontes = FonteProdutoSeedService().carregar_de_arquivo(
        Path("data/fontes_produtos.example.json")
    )
    categorias = {fonte.categoria for fonte in fontes}
    lojas_por_categoria = {
        categoria: {fonte.loja for fonte in fontes if fonte.categoria == categoria}
        for categoria in categorias
    }

    assert categorias == {nicho.value for nicho in NichoProduto}
    assert all(
        lojas == {LojaCupom.AMAZON, LojaCupom.MERCADO_LIVRE}
        for lojas in lojas_por_categoria.values()
    )
