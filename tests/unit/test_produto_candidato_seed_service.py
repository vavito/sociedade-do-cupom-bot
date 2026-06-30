import json
from datetime import date
from decimal import Decimal

import pytest

from src.dto.cupom_dto import LojaCupom
from src.service.produto_candidato_seed_service import ProdutoCandidatoSeedService


def test_carregar_produtos_candidatos_de_json(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "produtos.json"
    caminho.write_text(
        json.dumps(
            [
                {
                    "loja": "amazon",
                    "external_id": "amazon-monitor",
                    "titulo": "Monitor gamer 24 polegadas",
                    "url": "https://www.amazon.com.br/produto",
                    "preco": "999.90",
                    "categoria": "monitor",
                    "comissao_percentual": "4.5",
                }
            ]
        ),
        encoding="utf-8",
    )

    produtos = ProdutoCandidatoSeedService().carregar_de_arquivo(
        caminho,
        data_referencia=date(2026, 6, 30),
    )

    assert len(produtos) == 1
    assert produtos[0].loja == LojaCupom.AMAZON
    assert produtos[0].preco == Decimal("999.90")
    assert produtos[0].comissao_percentual == Decimal("4.5")
    assert produtos[0].data_referencia == date(2026, 6, 30)


def test_rejeita_json_que_nao_e_lista(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "produtos.json"
    caminho.write_text(json.dumps({"loja": "amazon"}), encoding="utf-8")

    with pytest.raises(ValueError, match="precisa conter uma lista"):
        ProdutoCandidatoSeedService().carregar_de_arquivo(caminho)
