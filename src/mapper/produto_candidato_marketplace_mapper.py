import hashlib
import html
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin

from src.dto.cupom_dto import LojaCupom
from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO


def mapear_produtos_marketplace(
    html_text: str,
    fonte: FonteProdutoDTO,
) -> list[ProdutoCandidatoDTO]:
    if fonte.loja == LojaCupom.AMAZON:
        return _mapear_blocos(_extrair_blocos_amazon(html_text), fonte, "https://www.amazon.com.br")
    if fonte.loja == LojaCupom.MERCADO_LIVRE:
        return _mapear_blocos(
            _extrair_blocos_mercado_livre(html_text),
            fonte,
            "https://www.mercadolivre.com.br",
        )
    return []


def _mapear_blocos(
    blocos: list[str],
    fonte: FonteProdutoDTO,
    base_url: str,
) -> list[ProdutoCandidatoDTO]:
    produtos = []
    marcas_por_nome: dict[str, int] = {}

    for bloco in blocos:
        produto = _mapear_bloco(bloco, fonte, base_url)
        if produto is None:
            continue

        marca_chave = produto.marca.casefold() if produto.marca else ""
        if marca_chave and fonte.limite_por_marca:
            total_marca = marcas_por_nome.get(marca_chave, 0)
            if total_marca >= fonte.limite_por_marca:
                continue
            marcas_por_nome[marca_chave] = total_marca + 1

        produtos.append(produto)

    return produtos


def _mapear_bloco(
    bloco: str,
    fonte: FonteProdutoDTO,
    base_url: str,
) -> ProdutoCandidatoDTO | None:
    if fonte.ignorar_patrocinados and _bloco_patrocinado(bloco):
        return None

    titulo = _extrair_titulo(bloco)
    url = _extrair_url(bloco, base_url)
    preco = _extrair_preco(bloco)
    if not titulo or not url or preco is None:
        return None

    if not _produto_passa_filtros(titulo, preco, fonte):
        return None

    marca = _extrair_marca(titulo, fonte)
    if fonte.exigir_marca_prioritaria and marca is None:
        return None
    if marca and marca.casefold() in {item.casefold() for item in fonte.marcas_bloqueadas}:
        return None

    return ProdutoCandidatoDTO(
        loja=fonte.loja,
        external_id=_external_id(fonte.loja, bloco, url),
        titulo=titulo,
        url=url,
        preco=preco,
        imagem_url=_extrair_imagem(bloco),
        categoria=fonte.categoria,
        marca=marca,
        raw_data={
            "fonte_url": str(fonte.url),
            "patrocinado": _bloco_patrocinado(bloco),
        },
    )


def _extrair_blocos_amazon(html_text: str) -> list[str]:
    markers = list(
        re.finditer(
            r"<div\b(?=[^>]*data-asin=)(?=[^>]*data-component-type=\"s-search-result\")[^>]*>",
            html_text,
            flags=re.IGNORECASE,
        )
    )
    return _fatiar_blocos(html_text, markers)


def _extrair_blocos_mercado_livre(html_text: str) -> list[str]:
    markers = list(
        re.finditer(
            r"<li\b(?=[^>]*ui-search-layout__item)[^>]*>",
            html_text,
            flags=re.IGNORECASE,
        )
    )
    return _fatiar_blocos(html_text, markers)


def _fatiar_blocos(html_text: str, markers: list[re.Match[str]]) -> list[str]:
    blocos = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(html_text)
        blocos.append(html_text[marker.start() : end])
    return blocos


def _extrair_titulo(bloco: str) -> str | None:
    patterns = [
        r"<h2[^>]*>.*?<span[^>]*>(.*?)</span>.*?</h2>",
        r"<h2[^>]*class=\"[^\"]*(?:ui-search-item__title|poly-component__title)[^\"]*\"[^>]*>(.*?)</h2>",
        r"<a[^>]+title=\"([^\"]+)\"",
        r"<img[^>]+alt=\"([^\"]+)\"",
    ]
    for pattern in patterns:
        match = re.search(pattern, bloco, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return _limpar_texto(match.group(1))
    return None


def _extrair_url(bloco: str, base_url: str) -> str | None:
    for match in re.finditer(r"<a[^>]+href=\"([^\"]+)\"", bloco, flags=re.IGNORECASE):
        link = match.group(1)
        if not link or link.startswith("#"):
            continue
        return urljoin(base_url, html.unescape(link))
    return None


def _extrair_preco(bloco: str) -> Decimal | None:
    preco_estruturado = _extrair_preco_estruturado(bloco)
    if preco_estruturado is not None:
        return preco_estruturado

    texto = _limpar_texto(bloco)
    match = re.search(r"R\$\s*([\d\.]+)(?:,(\d{1,2}))?", texto)
    if not match:
        return None

    valor = match.group(1).replace(".", "")
    centavos = (match.group(2) or "00").ljust(2, "0")
    try:
        return Decimal(f"{valor}.{centavos}")
    except InvalidOperation:
        return None


def _extrair_preco_estruturado(bloco: str) -> Decimal | None:
    fraction_match = re.search(
        r"class=\"[^\"]*andes-money-amount__fraction[^\"]*\"[^>]*>([\d\.]+)<",
        bloco,
        flags=re.IGNORECASE,
    )
    if not fraction_match:
        return None

    cents_match = re.search(
        r"class=\"[^\"]*andes-money-amount__cents[^\"]*\"[^>]*>(\d{1,2})<",
        bloco,
        flags=re.IGNORECASE,
    )
    valor = fraction_match.group(1).replace(".", "")
    centavos = (cents_match.group(1) if cents_match else "00").ljust(2, "0")
    try:
        return Decimal(f"{valor}.{centavos}")
    except InvalidOperation:
        return None


def _extrair_imagem(bloco: str) -> str | None:
    patterns = [
        r"<img[^>]+(?:src|data-src)=\"([^\"]+)\"[^>]*class=\"[^\"]*s-image[^\"]*\"",
        r"<img[^>]+(?:data-src|src)=\"([^\"]+)\"",
    ]
    for pattern in patterns:
        match = re.search(pattern, bloco, flags=re.IGNORECASE)
        if match:
            return html.unescape(match.group(1))
    return None


def _produto_passa_filtros(titulo: str, preco: Decimal, fonte: FonteProdutoDTO) -> bool:
    texto = _normalizar(titulo)
    if fonte.preco_minimo is not None and preco < fonte.preco_minimo:
        return False
    if fonte.preco_maximo is not None and preco > fonte.preco_maximo:
        return False
    if any(_normalizar(palavra) not in texto for palavra in fonte.palavras_obrigatorias):
        return False
    return not any(_normalizar(palavra) in texto for palavra in fonte.palavras_bloqueadas)


def _extrair_marca(titulo: str, fonte: FonteProdutoDTO) -> str | None:
    texto = _normalizar(titulo)
    for marca in fonte.marcas_prioritarias:
        if _normalizar(marca) in texto:
            return marca
    return None


def _external_id(loja: LojaCupom, bloco: str, url: str) -> str:
    if loja == LojaCupom.AMAZON:
        asin = _extrair_atributo(bloco, "data-asin")
        if asin:
            return f"amazon-{asin.lower()}"

    mercado_livre_id = re.search(r"\b(MLB-?\d+)\b", url, flags=re.IGNORECASE)
    if mercado_livre_id:
        return f"ml-{mercado_livre_id.group(1).replace('-', '').lower()}"

    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    return f"{loja}-{digest}"


def _extrair_atributo(bloco: str, atributo: str) -> str | None:
    match = re.search(rf"{atributo}=\"([^\"]+)\"", bloco, flags=re.IGNORECASE)
    return html.unescape(match.group(1)) if match else None


def _bloco_patrocinado(bloco: str) -> bool:
    texto = _normalizar(_limpar_texto(bloco))
    return "patrocinado" in texto or "sponsored" in texto


def _limpar_texto(texto_html: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", texto_html)
    texto = html.unescape(texto)
    return re.sub(r"\s+", " ", texto).strip()


def _normalizar(texto: str) -> str:
    substituicoes = str.maketrans("áàãâéêíóôõúç", "aaaaeeiooouc")
    return texto.casefold().translate(substituicoes)
