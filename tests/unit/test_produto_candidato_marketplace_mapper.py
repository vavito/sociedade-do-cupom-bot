from decimal import Decimal

from src.dto.cupom_dto import LojaCupom
from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.mapper.produto_candidato_marketplace_mapper import (
    diagnosticar_produtos_marketplace,
    mapear_produtos_marketplace,
)


def criar_fonte(
    loja: LojaCupom,
    categoria: str,
    palavras_obrigatorias: list[str],
    preco_minimo: Decimal = Decimal("100"),
    preco_maximo: Decimal = Decimal("1000"),
    limite_por_marca: int | None = 1,
    exigir_marca_prioritaria: bool = False,
) -> FonteProdutoDTO:
    return FonteProdutoDTO(
        loja=loja,
        categoria=categoria,
        url="https://example.com/busca",
        preco_minimo=preco_minimo,
        preco_maximo=preco_maximo,
        palavras_obrigatorias=palavras_obrigatorias,
        palavras_bloqueadas=["membrana"],
        marcas_prioritarias=["redragon", "logitech"],
        limite_por_marca=limite_por_marca,
        exigir_marca_prioritaria=exigir_marca_prioritaria,
    )


def test_mapeia_produtos_amazon_filtrando_patrocinado_e_membrana() -> None:
    html = """
    <div data-component-type="s-search-result" data-asin="B001">
      <span>Patrocinado</span>
      <h2><span>Headset Gamer Redragon Zeus</span></h2>
      <a href="/dp/B001"></a>
      <span class="a-offscreen">R$ 299,90</span>
      <img class="s-image" src="https://example.com/patrocinado.jpg" />
    </div>
    <div data-component-type="s-search-result" data-asin="B002">
      <h2><span>Teclado Gamer de Membrana</span></h2>
      <a href="/dp/B002"></a>
      <span class="a-offscreen">R$ 159,90</span>
      <img class="s-image" src="https://example.com/membrana.jpg" />
    </div>
    <div data-component-type="s-search-result" data-asin="B003">
      <h2><span>Teclado Mecânico Redragon Kumara</span></h2>
      <a href="/dp/B003"></a>
      <span class="a-offscreen">R$ 249,90</span>
      <img class="s-image" src="https://example.com/kumara.jpg" />
    </div>
    """

    produtos = mapear_produtos_marketplace(
        html,
        criar_fonte(LojaCupom.AMAZON, "teclado", ["teclado", "mecanico"]),
    )

    assert len(produtos) == 1
    assert produtos[0].external_id == "amazon-b003"
    assert produtos[0].titulo == "Teclado Mecânico Redragon Kumara"
    assert produtos[0].url == "https://www.amazon.com.br/dp/B003"
    assert produtos[0].preco == Decimal("249.90")
    assert produtos[0].imagem_url == "https://example.com/kumara.jpg"
    assert produtos[0].categoria == "teclado"
    assert produtos[0].marca == "redragon"


def test_mapeia_produtos_mercado_livre_com_faixa_de_preco() -> None:
    html = """
    <li class="ui-search-layout__item">
      <a href="https://www.mercadolivre.com.br/headset-gamer-logitech/p/MLB123456">
        <h2 class="poly-component__title">Headset Gamer Logitech G435</h2>
      </a>
      <span class="andes-money-amount">
        <span class="andes-money-amount__currency-symbol">R$</span>
        <span class="andes-money-amount__fraction">399</span>
        <span class="andes-money-amount__cents">90</span>
      </span>
      <img data-src="https://example.com/g435.jpg" />
    </li>
    <li class="ui-search-layout__item">
      <a href="https://www.mercadolivre.com.br/headset-gamer-caro/p/MLB999999">
        <h2 class="poly-component__title">Headset Gamer Logitech Astro</h2>
      </a>
      <span class="andes-money-amount">
        <span class="andes-money-amount__currency-symbol">R$</span>
        <span class="andes-money-amount__fraction">1.399</span>
        <span class="andes-money-amount__cents">90</span>
      </span>
      <img data-src="https://example.com/astro.jpg" />
    </li>
    """

    produtos = mapear_produtos_marketplace(
        html,
        criar_fonte(LojaCupom.MERCADO_LIVRE, "headset_fone", ["headset"]),
    )

    assert len(produtos) == 1
    assert produtos[0].external_id == "ml-mlb123456"
    assert produtos[0].titulo == "Headset Gamer Logitech G435"
    assert produtos[0].preco == Decimal("399.90")
    assert produtos[0].marca == "logitech"


def test_rejeita_patrocinado_mercado_livre_por_url_de_anuncio() -> None:
    html = """
    <li class="ui-search-layout__item">
      <a href="https://click1.mercadolivre.com.br/mclics/clicks/external/MLB/count?is_advertising=true&type=pad&wid=MLB111111">
        <h2 class="poly-component__title">Teclado MecÃ¢nico Redragon Dark Avenger</h2>
      </a>
      <span class="andes-money-amount">
        <span class="andes-money-amount__fraction">299</span>
        <span class="andes-money-amount__cents">90</span>
      </span>
    </li>
    <li class="ui-search-layout__item">
      <a href="https://www.mercadolivre.com.br/teclado-mecanico-redragon/p/MLB222222">
        <h2 class="poly-component__title">Teclado MecÃ¢nico Redragon Kumara</h2>
      </a>
      <span class="andes-money-amount">
        <span class="andes-money-amount__fraction">249</span>
        <span class="andes-money-amount__cents">90</span>
      </span>
    </li>
    """

    diagnostico = diagnosticar_produtos_marketplace(
        html,
        criar_fonte(LojaCupom.MERCADO_LIVRE, "teclado", ["teclado", "mecanico"]),
    )

    assert [produto.external_id for produto in diagnostico.produtos] == ["ml-mlb222222"]
    assert diagnostico.rejeicoes["patrocinado"] == 1


def test_limita_quantidade_por_marca_prioritaria() -> None:
    html = """
    <div data-component-type="s-search-result" data-asin="B001">
      <h2><span>Headset Gamer Redragon Zeus X</span></h2>
      <a href="/dp/B001"></a>
      <span class="a-offscreen">R$ 299,90</span>
    </div>
    <div data-component-type="s-search-result" data-asin="B002">
      <h2><span>Headset Gamer Redragon Lamia</span></h2>
      <a href="/dp/B002"></a>
      <span class="a-offscreen">R$ 199,90</span>
    </div>
    """

    produtos = mapear_produtos_marketplace(
        html,
        criar_fonte(LojaCupom.AMAZON, "headset_fone", ["headset"], limite_por_marca=1),
    )

    assert [produto.external_id for produto in produtos] == ["amazon-b001"]


def test_rejeita_produto_sem_marca_quando_fonte_exige_marca_prioritaria() -> None:
    html = """
    <div data-component-type="s-search-result" data-asin="B001">
      <h2><span>Teclado Mecânico Gamer com Fio 95 Teclas</span></h2>
      <a href="/dp/B001"></a>
      <span class="a-offscreen">R$ 199,90</span>
    </div>
    <div data-component-type="s-search-result" data-asin="B002">
      <h2><span>Teclado Mecânico Gamer Redragon Kumara</span></h2>
      <a href="/dp/B002"></a>
      <span class="a-offscreen">R$ 249,90</span>
    </div>
    """

    produtos = mapear_produtos_marketplace(
        html,
        criar_fonte(
            LojaCupom.AMAZON,
            "teclado",
            ["teclado", "mecanico"],
            exigir_marca_prioritaria=True,
        ),
    )

    assert [produto.external_id for produto in produtos] == ["amazon-b002"]


def test_filtro_de_palavras_ignora_acentos_reais() -> None:
    html = """
    <div data-component-type="s-search-result" data-asin="B004">
      <h2><span>Teclado Mecânico Redragon Kumara</span></h2>
      <a href="/dp/B004"></a>
      <span class="a-offscreen">R$ 249,90</span>
    </div>
    """

    produtos = mapear_produtos_marketplace(
        html,
        criar_fonte(LojaCupom.AMAZON, "teclado", ["teclado", "mecanico"]),
    )

    assert [produto.external_id for produto in produtos] == ["amazon-b004"]


def test_diagnostico_conta_rejeicoes_por_motivo() -> None:
    html = """
    <div data-component-type="s-search-result" data-asin="B001">
      <span>Patrocinado</span>
      <h2><span>Headset Gamer Redragon Zeus</span></h2>
      <a href="/dp/B001"></a>
      <span class="a-offscreen">R$ 299,90</span>
    </div>
    <div data-component-type="s-search-result" data-asin="B002">
      <h2><span>Teclado Gamer de Membrana</span></h2>
      <a href="/dp/B002"></a>
      <span class="a-offscreen">R$ 159,90</span>
    </div>
    <div data-component-type="s-search-result" data-asin="B003">
      <h2><span>Teclado Mecânico Redragon Kumara</span></h2>
      <a href="/dp/B003"></a>
      <span class="a-offscreen">R$ 249,90</span>
    </div>
    <div data-component-type="s-search-result" data-asin="B004">
      <h2><span>Teclado Mecânico Redragon Fizz</span></h2>
      <a href="/dp/B004"></a>
      <span class="a-offscreen">R$ 229,90</span>
    </div>
    """

    diagnostico = diagnosticar_produtos_marketplace(
        html,
        criar_fonte(
            LojaCupom.AMAZON,
            "teclado",
            ["teclado", "mecanico"],
            limite_por_marca=1,
        ),
    )

    assert diagnostico.total_blocos == 4
    assert [produto.external_id for produto in diagnostico.produtos] == ["amazon-b003"]
    assert diagnostico.rejeicoes == {
        "patrocinado": 1,
        "palavra_obrigatoria_ausente": 1,
        "limite_por_marca": 1,
    }
