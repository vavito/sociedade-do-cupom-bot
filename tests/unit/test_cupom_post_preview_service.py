from datetime import date
from decimal import Decimal
from pathlib import Path

from src.dto.cupom_dto import CupomDTO, LojaCupom, TipoDescontoCupom
from src.dto.cupom_produto_match_dto import CupomProdutoMatchDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.cupom_post_preview_service import CupomPostPreviewService


def criar_match() -> CupomProdutoMatchDTO:
    cupom = CupomDTO(
        fonte="thiago_rodrigo",
        loja=LojaCupom.AMAZON,
        titulo="Cupom Amazon de 10% de desconto",
        codigo="CRAQUE10",
        data=date(2026, 6, 30),
        desconto_tipo=TipoDescontoCupom.PERCENTUAL,
        desconto_valor=Decimal("10"),
        valor_minimo=Decimal("250"),
        limite_desconto=Decimal("50"),
    )
    produto = ProdutoCandidatoDTO(
        loja=LojaCupom.AMAZON,
        external_id="monitor",
        titulo="Monitor gamer LG 24 polegadas",
        url="https://www.amazon.com.br/produto",
        preco=Decimal("999.90"),
        imagem_url="https://example.com/monitor.jpg",
        categoria="monitor",
        data_referencia=date(2026, 6, 30),
    )
    return CupomProdutoMatchDTO(
        cupom=cupom,
        produto=produto,
        desconto_estimado=Decimal("50.00"),
        preco_estimado=Decimal("949.90"),
        score=80,
        motivo="teste",
    )


def test_gera_preview_de_post_de_cupom_com_produto() -> None:
    mensagem = CupomPostPreviewService().gerar(criar_match())

    assert mensagem.image_url is not None
    image_path = Path(str(mensagem.image_url))
    assert image_path.name == "banner_telegram_amazon.jpg"
    assert image_path.is_file()
    assert "Cupom Amazon: CRAQUE10" in mensagem.caption
    assert "10% OFF, acima de R$ 250, limite R$ 50" in mensagem.caption
    assert "preco estimado" not in mensagem.caption
    assert "Produto sugerido" not in mensagem.caption
    assert "Ative por aqui para ajudar o grupo: https://www.amazon.com.br/produto" in (
        mensagem.caption
    )
    assert mensagem.caption.endswith("(Anuncio)")


def test_gera_preview_de_cupom_mercado_livre_com_banner_da_loja() -> None:
    match = criar_match()
    match.cupom.loja = LojaCupom.MERCADO_LIVRE
    match.produto.loja = LojaCupom.MERCADO_LIVRE

    mensagem = CupomPostPreviewService().gerar(match)

    assert mensagem.image_url is not None
    image_path = Path(str(mensagem.image_url))
    assert image_path.name == "banner_telegram_mercadolivre.jpg"
    assert image_path.is_file()
    assert "Cupom Mercado Livre: CRAQUE10" in mensagem.caption
