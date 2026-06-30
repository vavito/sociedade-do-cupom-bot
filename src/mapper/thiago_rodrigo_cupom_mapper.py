import html
import re
from datetime import date, datetime
from typing import Any

from src.dto.cupom_dto import CupomDTO, LojaCupom

FONTE_THIAGO_RODRIGO = "thiago_rodrigo"


def mapear_cupons_thiago_rodrigo(
    html_text: str,
    loja: LojaCupom,
    source_url: str,
) -> list[CupomDTO]:
    cupons = []
    vistos = set()

    for bloco in _extrair_blocos_cupom(html_text):
        cupom = _mapear_bloco_cupom(bloco, loja, source_url)
        if cupom is None:
            continue

        chave = (cupom.loja, cupom.codigo, cupom.titulo, cupom.data)
        if chave in vistos:
            continue
        vistos.add(chave)
        cupons.append(cupom)

    return cupons


def _extrair_blocos_cupom(html_text: str) -> list[str]:
    return re.findall(
        r'<li\s+class="[^"]*\bcoupon\b[^"]*"[^>]*>.*?</li>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )


def _mapear_bloco_cupom(bloco: str, loja: LojaCupom, source_url: str) -> CupomDTO | None:
    titulo = _extrair_texto_por_classe(bloco, "coupon-title")
    if not titulo:
        return None

    descricao = _extrair_texto_por_classe(bloco, "coupon-description")
    codigo = _extrair_atributo(bloco, "data-full-code")
    link_resgate = _extrair_atributo(bloco, "data-target-url")
    data_cupom = _extrair_data(bloco)
    tipo = _extrair_tipo(bloco)

    return CupomDTO(
        fonte=FONTE_THIAGO_RODRIGO,
        loja=loja,
        titulo=titulo,
        descricao=descricao,
        codigo=codigo,
        data=data_cupom,
        tipo=tipo,
        link_resgate=link_resgate,
        raw_data={
            "source_url": source_url,
            "html_snippet": bloco[:1500],
        },
    )


def _extrair_texto_por_classe(bloco: str, classe: str) -> str | None:
    pattern = rf'<[^>]+class="[^"]*\b{re.escape(classe)}\b[^"]*"[^>]*>(.*?)</[^>]+>'
    match = re.search(pattern, bloco, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return _limpar_texto(match.group(1))


def _extrair_atributo(bloco: str, atributo: str) -> str | None:
    match = re.search(
        rf'{re.escape(atributo)}\s*=\s*(["\'])(.*?)\1',
        bloco,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    valor = html.unescape(match.group(2)).strip()
    return valor or None


def _extrair_data(bloco: str) -> date | None:
    match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", bloco)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%d/%m/%Y").date()
    except ValueError:
        return None


def _extrair_tipo(bloco: str) -> str | None:
    textos = re.findall(
        r'<span\s+class="text-icone"[^>]*>(.*?)</span>',
        bloco,
        flags=re.IGNORECASE | re.DOTALL,
    )
    for texto in textos:
        limpo = _limpar_texto(texto)
        if limpo and not re.fullmatch(r"\d{2}/\d{2}/\d{4}", limpo):
            return limpo
    return None


def _limpar_texto(texto_html: Any) -> str:
    texto = re.sub(r"<[^>]+>", " ", str(texto_html))
    texto = html.unescape(texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()
