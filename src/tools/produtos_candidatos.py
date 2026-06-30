import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from src.dto.cupom_dto import LojaCupom
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.nicho_produto_service import NichoProdutoService
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService


def main() -> None:
    args = _parse_args()
    service = ProdutoCandidatoCatalogoService()

    if args.comando == "listar":
        _listar(service, args.arquivo)
        return

    if args.comando == "adicionar":
        produto = _construir_produto(args)
        produtos = service.adicionar(args.arquivo, produto, substituir=args.substituir)
        print(f"Produto salvo: {service.chave_produto(produto)}")
        print(f"Total de produtos candidatos: {len(produtos)}")
        return

    if args.comando == "remover":
        removido = service.remover(args.arquivo, LojaCupom(args.loja), args.external_id)
        if removido:
            print(f"Produto removido: {args.loja}:{args.external_id}")
        else:
            print(f"Produto nao encontrado: {args.loja}:{args.external_id}")


def _listar(service: ProdutoCandidatoCatalogoService, caminho: Path) -> None:
    produtos = service.listar(caminho)
    print(f"Produtos candidatos: {len(produtos)}")
    for produto in produtos:
        print(
            " | ".join(
                [
                    service.chave_produto(produto),
                    produto.categoria or "sem_categoria",
                    f"R$ {_formatar_decimal(produto.preco)}",
                    produto.titulo,
                ]
            )
        )


def _construir_produto(args: argparse.Namespace) -> ProdutoCandidatoDTO:
    categoria = args.categoria or NichoProdutoService().classificar(
        args.titulo,
        marca=args.marca,
    )
    return ProdutoCandidatoDTO(
        loja=LojaCupom(args.loja),
        external_id=args.external_id,
        titulo=args.titulo,
        url=args.url,
        preco=_parse_decimal(args.preco),
        imagem_url=args.imagem_url,
        categoria=categoria,
        marca=args.marca,
        comissao_percentual=(
            _parse_decimal(args.comissao_percentual) if args.comissao_percentual else None
        ),
        data_referencia=(_parse_date(args.data_referencia) if args.data_referencia else None),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gerencia o JSON local de produtos candidatos para posts de cupom.",
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--arquivo",
        type=Path,
        default=Path("data/produtos_candidatos.json"),
        help="Caminho do JSON local de produtos candidatos.",
    )

    listar_parser = subparsers.add_parser("listar", parents=[parent])
    listar_parser.set_defaults(comando="listar")

    adicionar_parser = subparsers.add_parser("adicionar", parents=[parent])
    adicionar_parser.set_defaults(comando="adicionar")
    adicionar_parser.add_argument(
        "--loja", choices=[loja.value for loja in LojaCupom], required=True
    )
    adicionar_parser.add_argument("--external-id", required=True)
    adicionar_parser.add_argument("--titulo", required=True)
    adicionar_parser.add_argument("--url", required=True)
    adicionar_parser.add_argument("--preco", required=True)
    adicionar_parser.add_argument("--imagem-url")
    adicionar_parser.add_argument("--categoria")
    adicionar_parser.add_argument("--marca")
    adicionar_parser.add_argument("--comissao-percentual")
    adicionar_parser.add_argument("--data-referencia")
    adicionar_parser.add_argument("--substituir", action="store_true")

    remover_parser = subparsers.add_parser("remover", parents=[parent])
    remover_parser.set_defaults(comando="remover")
    remover_parser.add_argument("--loja", choices=[loja.value for loja in LojaCupom], required=True)
    remover_parser.add_argument("--external-id", required=True)

    return parser.parse_args()


def _parse_decimal(value: str) -> Decimal:
    try:
        return Decimal(value.replace(",", "."))
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("Valor decimal invalido.") from exc


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Data precisa estar no formato YYYY-MM-DD.") from exc


def _formatar_decimal(valor: Decimal) -> str:
    texto = f"{valor:.0f}" if valor == valor.to_integral() else f"{valor:.2f}"
    return texto.replace(".", ",")


if __name__ == "__main__":
    main()
