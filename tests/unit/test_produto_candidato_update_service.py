import json
from datetime import date
from decimal import Decimal

from src.dto.cupom_dto import LojaCupom
from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.produto_candidato_update_service import ProdutoCandidatoUpdateService


class FakeScraperService:
    def __init__(self, produtos: list[ProdutoCandidatoDTO]) -> None:
        self.produtos = produtos
        self.data_referencia: date | None = None
        self.limite_por_fonte: int | None = None

    async def buscar_produtos(
        self,
        fontes: list[FonteProdutoDTO],
        data_referencia: date | None = None,
        limite_por_fonte: int = 10,
    ) -> list[ProdutoCandidatoDTO]:
        self.data_referencia = data_referencia
        self.limite_por_fonte = limite_por_fonte
        return self.produtos


def criar_fonte() -> FonteProdutoDTO:
    return FonteProdutoDTO(
        loja=LojaCupom.AMAZON,
        categoria="headset_fone",
        url="https://www.amazon.com.br/s?k=headset",
    )


def criar_produto(
    external_id: str,
    titulo: str,
    preco: Decimal,
) -> ProdutoCandidatoDTO:
    return ProdutoCandidatoDTO(
        loja=LojaCupom.AMAZON,
        external_id=external_id,
        titulo=titulo,
        url=f"https://www.amazon.com.br/{external_id}",
        preco=preco,
        categoria="headset_fone",
    )


async def test_atualizar_por_fontes_salva_produtos_encontrados(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho_saida = tmp_path / "produtos.json"
    produto = criar_produto("headset", "Headset Havit", Decimal("159.90"))
    scraper = FakeScraperService([produto])
    service = ProdutoCandidatoUpdateService(scraper)  # type: ignore[arg-type]

    resultado = await service.atualizar_por_fontes(
        fontes=[criar_fonte()],
        caminho_saida=caminho_saida,
        data_referencia=date(2026, 7, 1),
        limite_por_fonte=5,
        salvar=True,
    )

    payload = json.loads(caminho_saida.read_text(encoding="utf-8"))
    assert resultado.total_fontes == 1
    assert resultado.encontrados == [produto]
    assert resultado.produtos_finais == [produto]
    assert scraper.data_referencia == date(2026, 7, 1)
    assert scraper.limite_por_fonte == 5
    assert payload[0]["external_id"] == "headset"


async def test_atualizar_por_fontes_mantem_existentes_e_substitui_duplicados(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    caminho_saida = tmp_path / "produtos.json"
    antigo = criar_produto("headset", "Headset antigo", Decimal("199.90"))
    outro = criar_produto("teclado", "Teclado Redragon", Decimal("249.90"))
    ProdutoCandidatoUpdateService(
        FakeScraperService([])  # type: ignore[arg-type]
    ).catalogo_service.salvar(caminho_saida, [antigo, outro])

    novo = criar_produto("headset", "Headset novo", Decimal("159.90"))
    service = ProdutoCandidatoUpdateService(FakeScraperService([novo]))  # type: ignore[arg-type]

    resultado = await service.atualizar_por_fontes(
        fontes=[criar_fonte()],
        caminho_saida=caminho_saida,
        manter_existentes=True,
    )

    assert [produto.external_id for produto in resultado.produtos_finais] == [
        "headset",
        "teclado",
    ]
    assert resultado.produtos_finais[0].titulo == "Headset novo"
