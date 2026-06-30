from decimal import Decimal

from src.dto.cupom_dto import LojaCupom, TipoDescontoCupom
from src.dto.cupom_produto_match_dto import CupomProdutoMatchDTO
from src.dto.telegram_message_dto import TelegramMessageDTO


class CupomPostPreviewService:
    def gerar(self, match: CupomProdutoMatchDTO) -> TelegramMessageDTO:
        cupom = match.cupom
        produto = match.produto

        linhas = [
            f"\U0001f39f\ufe0f Cupom {self._nome_loja(cupom.loja)}: {cupom.codigo or cupom.titulo}",
            f"\U0001f4b5 {self._formatar_beneficio(match)}",
            "",
            f"\u2b50\ufe0f Ative por aqui para ajudar o grupo: {produto.url}",
        ]

        if cupom.somente_app:
            linhas.insert(2, "Somente aplicativo")
        if cupom.primeira_compra:
            linhas.insert(2, "Primeira compra")

        linhas.extend(["", "(Anuncio)"])
        return TelegramMessageDTO(image_url=produto.imagem_url, caption="\n".join(linhas))

    def _formatar_beneficio(self, match: CupomProdutoMatchDTO) -> str:
        cupom = match.cupom
        partes = []

        if cupom.desconto_tipo == TipoDescontoCupom.PERCENTUAL and cupom.desconto_valor:
            partes.append(f"{self._formatar_decimal(cupom.desconto_valor)}% OFF")
        elif cupom.desconto_tipo == TipoDescontoCupom.VALOR_FIXO and cupom.desconto_valor:
            partes.append(f"{self._formatar_moeda(cupom.desconto_valor)} OFF")
        elif cupom.desconto_tipo == TipoDescontoCupom.FRETE_GRATIS:
            partes.append("Frete gratis")
        else:
            partes.append(cupom.descricao or "Desconto no produto")

        if cupom.valor_minimo:
            partes.append(f"acima de {self._formatar_moeda(cupom.valor_minimo)}")
        if cupom.limite_desconto:
            partes.append(f"limite {self._formatar_moeda(cupom.limite_desconto)}")

        return ", ".join(partes)

    @staticmethod
    def _nome_loja(loja: LojaCupom) -> str:
        nomes = {
            LojaCupom.AMAZON: "Amazon",
            LojaCupom.MERCADO_LIVRE: "Mercado Livre",
            LojaCupom.KABUM: "KaBuM",
            LojaCupom.SHOPEE: "Shopee",
        }
        return nomes.get(loja, "Loja")

    @classmethod
    def _formatar_moeda(cls, valor: Decimal) -> str:
        return f"R$ {cls._formatar_decimal(valor)}"

    @staticmethod
    def _formatar_decimal(valor: Decimal) -> str:
        texto = f"{valor:.0f}" if valor == valor.to_integral() else f"{valor:.2f}"
        return texto.replace(".", ",")
