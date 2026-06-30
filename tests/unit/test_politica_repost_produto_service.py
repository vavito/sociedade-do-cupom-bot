from datetime import datetime

from src.service.politica_repost_produto_service import PoliticaRepostProdutoService


def test_permite_primeira_postagem_do_dia_mesmo_apos_18h() -> None:
    service = PoliticaRepostProdutoService()

    decisao = service.avaliar(
        postagens_anteriores=[datetime(2026, 6, 28, 20, 0)],
        agora=datetime(2026, 6, 29, 19, 0),
    )

    assert decisao.pode_postar


def test_bloqueia_repost_antes_de_6h() -> None:
    service = PoliticaRepostProdutoService()

    decisao = service.avaliar(
        postagens_anteriores=[datetime(2026, 6, 29, 9, 0)],
        agora=datetime(2026, 6, 29, 14, 59),
    )

    assert not decisao.pode_postar


def test_permite_repost_com_6h_no_mesmo_dia_antes_das_18h() -> None:
    service = PoliticaRepostProdutoService()

    decisao = service.avaliar(
        postagens_anteriores=[datetime(2026, 6, 29, 9, 0)],
        agora=datetime(2026, 6, 29, 15, 0),
    )

    assert decisao.pode_postar


def test_bloqueia_repost_apos_18h_quando_produto_ja_foi_postado_no_dia() -> None:
    service = PoliticaRepostProdutoService()

    decisao = service.avaliar(
        postagens_anteriores=[datetime(2026, 6, 29, 10, 0)],
        agora=datetime(2026, 6, 29, 18, 0),
    )

    assert not decisao.pode_postar


def test_ignora_postagens_de_dias_anteriores() -> None:
    service = PoliticaRepostProdutoService()

    decisao = service.avaliar(
        postagens_anteriores=[
            datetime(2026, 6, 27, 10, 0),
            datetime(2026, 6, 28, 17, 0),
        ],
        agora=datetime(2026, 6, 29, 9, 0),
    )

    assert decisao.pode_postar
