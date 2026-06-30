from decimal import ROUND_HALF_UP, Decimal

from src.dto.cupom_dto import CupomDTO, TipoDescontoCupom
from src.dto.cupom_produto_match_dto import CupomProdutoMatchDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO

PALAVRAS_TECH_PRODUTO = {
    "amd",
    "b550",
    "computador",
    "console",
    "cpu",
    "ddr4",
    "ddr5",
    "fone",
    "game",
    "gamer",
    "headset",
    "intel",
    "monitor",
    "mouse",
    "notebook",
    "nvme",
    "placa",
    "processador",
    "ryzen",
    "smartphone",
    "ssd",
    "teclado",
}


class CupomProdutoMatchService:
    def gerar_matches(
        self,
        cupons: list[CupomDTO],
        produtos: list[ProdutoCandidatoDTO],
    ) -> list[CupomProdutoMatchDTO]:
        matches = []
        for cupom in cupons:
            for produto in produtos:
                match = self.gerar_match(cupom, produto)
                if match is not None:
                    matches.append(match)

        return sorted(matches, key=lambda item: item.score, reverse=True)

    def gerar_match(
        self,
        cupom: CupomDTO,
        produto: ProdutoCandidatoDTO,
    ) -> CupomProdutoMatchDTO | None:
        if cupom.loja != produto.loja:
            return None

        if cupom.data and produto.data_referencia and cupom.data != produto.data_referencia:
            return None

        if cupom.valor_minimo and produto.preco < cupom.valor_minimo:
            return None

        if not self._categoria_compativel(cupom, produto):
            return None

        desconto = self._calcular_desconto(cupom, produto)
        if desconto <= 0 and cupom.desconto_tipo != TipoDescontoCupom.FRETE_GRATIS:
            return None

        preco_estimado = max(Decimal("0"), produto.preco - desconto)
        score = self._calcular_score(cupom, produto, desconto)
        return CupomProdutoMatchDTO(
            cupom=cupom,
            produto=produto,
            desconto_estimado=self._arredondar(desconto),
            preco_estimado=self._arredondar(preco_estimado),
            score=score,
            motivo=self._montar_motivo(cupom, produto, desconto),
        )

    @staticmethod
    def _calcular_desconto(cupom: CupomDTO, produto: ProdutoCandidatoDTO) -> Decimal:
        if cupom.desconto_tipo == TipoDescontoCupom.PERCENTUAL and cupom.desconto_valor:
            desconto = produto.preco * cupom.desconto_valor / Decimal("100")
            if cupom.limite_desconto:
                desconto = min(desconto, cupom.limite_desconto)
            return desconto

        if cupom.desconto_tipo == TipoDescontoCupom.VALOR_FIXO and cupom.desconto_valor:
            return min(cupom.desconto_valor, produto.preco)

        return Decimal("0")

    @classmethod
    def _calcular_score(
        cls,
        cupom: CupomDTO,
        produto: ProdutoCandidatoDTO,
        desconto: Decimal,
    ) -> int:
        score = min(int(desconto), 60)

        if produto.preco > 0:
            percentual_efetivo = int((desconto / produto.preco) * 100)
            score += min(percentual_efetivo, 25)

        if produto.comissao_percentual:
            score += min(int(produto.comissao_percentual), 10)

        if cls._produto_tech(produto):
            score += 10

        if cupom.somente_app:
            score -= 5
        if cupom.primeira_compra:
            score -= 10

        return max(0, min(score, 100))

    @classmethod
    def _categoria_compativel(cls, cupom: CupomDTO, produto: ProdutoCandidatoDTO) -> bool:
        if cupom.categoria_hint is None or cupom.categoria_hint == "mercado":
            return cls._produto_tech(produto)

        texto = cls._texto_produto(produto)
        if cupom.categoria_hint == "informatica":
            return cls._contem(texto, "informatica", "informática", "pc", "notebook", "placa")
        if cupom.categoria_hint == "games":
            return cls._contem(texto, "game", "gamer", "console", "headset")
        if cupom.categoria_hint == "smartphones":
            return cls._contem(texto, "smartphone", "celular", "iphone")
        return False

    @classmethod
    def _produto_tech(cls, produto: ProdutoCandidatoDTO) -> bool:
        texto = cls._texto_produto(produto)
        return any(palavra in texto for palavra in PALAVRAS_TECH_PRODUTO)

    @staticmethod
    def _texto_produto(produto: ProdutoCandidatoDTO) -> str:
        return f"{produto.titulo} {produto.categoria or ''} {produto.marca or ''}".casefold()

    @staticmethod
    def _contem(texto: str, *termos: str) -> bool:
        return any(termo in texto for termo in termos)

    @staticmethod
    def _arredondar(valor: Decimal) -> Decimal:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def _montar_motivo(
        cls,
        cupom: CupomDTO,
        produto: ProdutoCandidatoDTO,
        desconto: Decimal,
    ) -> str:
        partes = [f"mesma loja: {produto.loja}"]
        if cupom.valor_minimo:
            partes.append(f"preco acima do minimo: R$ {produto.preco}")
        if desconto > 0:
            partes.append(f"desconto estimado: R$ {cls._arredondar(desconto)}")
        if produto.comissao_percentual:
            partes.append(f"comissao: {produto.comissao_percentual}%")
        return "; ".join(partes)
