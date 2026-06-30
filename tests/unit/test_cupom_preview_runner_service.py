import json
from datetime import date, datetime
from decimal import Decimal

from src.dto.cupom_dto import CupomDTO, LojaCupom, TipoDescontoCupom
from src.service.cupom_preview_runner_service import CupomPreviewRunnerService


class FakeCupomScraperService:
    def __init__(self) -> None:
        self.filtrar: bool | None = None

    async def buscar_cupons_iniciais(self, filtrar: bool = True) -> list[CupomDTO]:
        self.filtrar = filtrar
        return [
            CupomDTO(
                fonte="thiago_rodrigo",
                loja=LojaCupom.AMAZON,
                titulo="Cupom Amazon",
                codigo="TECH100",
                data=date(2026, 6, 30),
                desconto_tipo=TipoDescontoCupom.VALOR_FIXO,
                desconto_valor=Decimal("100"),
                valor_minimo=Decimal("500"),
            )
        ]


async def test_runner_gera_previews_a_partir_de_cupons_e_produtos(tmp_path) -> None:  # type: ignore[no-untyped-def]
    caminho_produtos = tmp_path / "produtos.json"
    caminho_produtos.write_text(
        json.dumps(
            [
                {
                    "loja": "amazon",
                    "external_id": "amazon-monitor",
                    "titulo": "Monitor gamer 24 polegadas",
                    "url": "https://www.amazon.com.br/produto",
                    "preco": "999.90",
                    "categoria": "monitor",
                }
            ]
        ),
        encoding="utf-8",
    )
    scraper = FakeCupomScraperService()
    service = CupomPreviewRunnerService(scraper)  # type: ignore[arg-type]

    resultado = await service.gerar_previews(
        caminho_produtos,
        agora=datetime(2026, 6, 30, 10, 0),
        limite=1,
        filtrar_cupons=False,
    )

    assert scraper.filtrar is False
    assert resultado.total_cupons == 1
    assert resultado.total_produtos == 1
    assert resultado.total_previews == 1
    match, mensagem = resultado.previews[0]
    assert match.produto.data_referencia == date(2026, 6, 30)
    assert match.cupom.codigo == "TECH100"
    assert "Cupom Amazon: TECH100" in mensagem.caption
