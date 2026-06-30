import json
from datetime import datetime

import pytest

from src.service.cupom_postagem_historico_service import CupomPostagemHistoricoService


def test_carregar_historico_inexistente_retorna_vazio(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "historico.json"

    historico = CupomPostagemHistoricoService().carregar_de_arquivo(caminho)

    assert historico == {}


def test_salva_e_carrega_historico_de_postagens(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "historico.json"
    service = CupomPostagemHistoricoService()

    service.salvar_em_arquivo(
        caminho,
        {
            "amazon:monitor": [
                datetime(2026, 6, 30, 10, 0),
                datetime(2026, 6, 30, 16, 0),
            ]
        },
    )
    historico = service.carregar_de_arquivo(caminho)

    assert historico == {
        "amazon:monitor": [
            datetime(2026, 6, 30, 10, 0),
            datetime(2026, 6, 30, 16, 0),
        ]
    }


def test_registrar_postagem_preserva_historico_original() -> None:
    service = CupomPostagemHistoricoService()
    historico = {"amazon:monitor": [datetime(2026, 6, 30, 10, 0)]}

    atualizado = service.registrar_postagem(
        historico,
        "amazon:monitor",
        datetime(2026, 6, 30, 16, 0),
    )

    assert historico == {"amazon:monitor": [datetime(2026, 6, 30, 10, 0)]}
    assert atualizado == {
        "amazon:monitor": [
            datetime(2026, 6, 30, 10, 0),
            datetime(2026, 6, 30, 16, 0),
        ]
    }


def test_rejeita_historico_que_nao_e_objeto_json(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho = tmp_path / "historico.json"
    caminho.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(ValueError, match="precisa conter um objeto"):
        CupomPostagemHistoricoService().carregar_de_arquivo(caminho)
