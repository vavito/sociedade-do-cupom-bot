import json
from decimal import Decimal

import pytest

from src.dto.cupom_dto import LojaCupom
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService


def criar_produto(
    external_id: str = "monitor",
    titulo: str = "Monitor gamer 24 polegadas",
    preco: Decimal = Decimal("999.90"),
) -> ProdutoCandidatoDTO:
    return ProdutoCandidatoDTO(
        loja=LojaCupom.AMAZON,
        external_id=external_id,
        titulo=titulo,
        url="https://www.amazon.com.br/produto",
        preco=preco,
        categoria="monitor",
        marca="LG",
        comissao_percentual=Decimal("4"),
    )


def test_listar_catalogo_inexistente_retorna_vazio(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "produtos.json"

    produtos = ProdutoCandidatoCatalogoService().listar(caminho)

    assert produtos == []


def test_adicionar_produto_candidato_salva_json(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "produtos.json"
    service = ProdutoCandidatoCatalogoService()

    produtos = service.adicionar(caminho, criar_produto())
    payload = json.loads(caminho.read_text(encoding="utf-8"))

    assert len(produtos) == 1
    assert payload[0]["loja"] == "amazon"
    assert payload[0]["external_id"] == "monitor"
    assert payload[0]["preco"] == "999.90"
    assert "raw_data" not in payload[0]


def test_rejeita_produto_duplicado_sem_substituir(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "produtos.json"
    service = ProdutoCandidatoCatalogoService()
    service.adicionar(caminho, criar_produto())

    with pytest.raises(ValueError, match="ja existe"):
        service.adicionar(caminho, criar_produto())


def test_substitui_produto_existente(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "produtos.json"
    service = ProdutoCandidatoCatalogoService()
    service.adicionar(caminho, criar_produto())

    produtos = service.adicionar(
        caminho,
        criar_produto(titulo="Monitor LG 180Hz", preco=Decimal("899.90")),
        substituir=True,
    )

    assert len(produtos) == 1
    assert produtos[0].titulo == "Monitor LG 180Hz"
    assert produtos[0].preco == Decimal("899.90")


def test_remove_produto_candidato(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "produtos.json"
    service = ProdutoCandidatoCatalogoService()
    service.adicionar(caminho, criar_produto())

    removido = service.remover(caminho, LojaCupom.AMAZON, "monitor")

    assert removido is True
    assert service.listar(caminho) == []


def test_remover_produto_inexistente_retorna_false(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "produtos.json"

    removido = ProdutoCandidatoCatalogoService().remover(
        caminho,
        LojaCupom.AMAZON,
        "monitor",
    )

    assert removido is False
