import argparse

from src.dto.cupom_dto import LojaCupom
from src.dto.fonte_produto_dto import FonteProdutoDTO


def adicionar_argumentos_filtro_fontes(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--loja",
        dest="lojas",
        action="append",
        choices=[LojaCupom.AMAZON.value, LojaCupom.MERCADO_LIVRE.value],
        help="Filtra uma loja especifica. Pode ser repetido.",
    )
    parser.add_argument(
        "--categoria",
        dest="categorias",
        action="append",
        help="Filtra uma categoria especifica. Pode ser repetido.",
    )


def filtrar_fontes(
    fontes: list[FonteProdutoDTO],
    lojas: list[str] | None = None,
    categorias: list[str] | None = None,
) -> list[FonteProdutoDTO]:
    lojas_normalizadas = {loja.casefold() for loja in lojas or []}
    categorias_normalizadas = {categoria.casefold() for categoria in categorias or []}
    return [
        fonte
        for fonte in fontes
        if (not lojas_normalizadas or fonte.loja.casefold() in lojas_normalizadas)
        and (not categorias_normalizadas or fonte.categoria.casefold() in categorias_normalizadas)
    ]
