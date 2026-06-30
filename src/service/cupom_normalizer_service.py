import re
from decimal import Decimal, InvalidOperation

from src.dto.cupom_dto import CupomDTO, TipoDescontoCupom


class CupomNormalizerService:
    def normalizar(self, cupom: CupomDTO) -> CupomDTO:
        texto = self._texto_busca(cupom)
        desconto_tipo, desconto_valor = self._extrair_desconto(texto)

        return cupom.model_copy(
            update={
                "codigo": self._normalizar_codigo(cupom.codigo),
                "desconto_tipo": desconto_tipo,
                "desconto_valor": desconto_valor,
                "valor_minimo": self._extrair_valor_minimo(texto),
                "limite_desconto": self._extrair_limite_desconto(texto),
                "somente_app": self._contem(texto, "somente aplicativo", "somente app"),
                "primeira_compra": self._contem(texto, "primeira compra", "1ª compra"),
                "exclusivo": self._contem(texto, "exclusivo", "exclusiva"),
                "categoria_hint": self._extrair_categoria_hint(texto),
            }
        )

    def normalizar_lista(self, cupons: list[CupomDTO]) -> list[CupomDTO]:
        return [self.normalizar(cupom) for cupom in cupons]

    @staticmethod
    def _texto_busca(cupom: CupomDTO) -> str:
        return f"{cupom.titulo} {cupom.descricao or ''}".casefold()

    @classmethod
    def _extrair_desconto(cls, texto: str) -> tuple[TipoDescontoCupom, Decimal | None]:
        percentual = re.search(r"(\d+(?:[,.]\d+)?)\s*%", texto)
        if percentual:
            return TipoDescontoCupom.PERCENTUAL, cls._parse_decimal(percentual.group(1))

        if "frete gratis" in cls._sem_acentos(texto) or "frete grátis" in texto:
            return TipoDescontoCupom.FRETE_GRATIS, None

        valor = re.search(r"r\$\s*(\d+(?:[,.]\d+)?)", texto)
        if valor:
            return TipoDescontoCupom.VALOR_FIXO, cls._parse_decimal(valor.group(1))

        return TipoDescontoCupom.DESCONHECIDO, None

    @classmethod
    def _extrair_valor_minimo(cls, texto: str) -> Decimal | None:
        patterns = [
            (
                r"(?:acima|a partir|comprando acima|compras acima|em compras acima)"
                r"\s+de\s+r\$\s*(\d+(?:[,.]\d+)?)"
            ),
            r"(?:mínimo|minimo)\s+de\s+r\$\s*(\d+(?:[,.]\d+)?)",
        ]
        return cls._extrair_primeiro_valor(texto, patterns)

    @classmethod
    def _extrair_limite_desconto(cls, texto: str) -> Decimal | None:
        patterns = [
            r"(?:limite|limitado)\s+(?:de\s+)?(?:a\s+)?r\$\s*(\d+(?:[,.]\d+)?)",
            r"até\s+r\$\s*(\d+(?:[,.]\d+)?)\s+(?:off|de desconto)",
        ]
        return cls._extrair_primeiro_valor(texto, patterns)

    @classmethod
    def _extrair_primeiro_valor(cls, texto: str, patterns: list[str]) -> Decimal | None:
        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                return cls._parse_decimal(match.group(1))
        return None

    @staticmethod
    def _normalizar_codigo(codigo: str | None) -> str | None:
        if not codigo:
            return None
        codigo = codigo.strip().upper()
        return codigo or None

    @staticmethod
    def _parse_decimal(valor: str) -> Decimal | None:
        try:
            return Decimal(valor.replace(",", "."))
        except InvalidOperation:
            return None

    @staticmethod
    def _contem(texto: str, *termos: str) -> bool:
        return any(termo in texto for termo in termos)

    @classmethod
    def _extrair_categoria_hint(cls, texto: str) -> str | None:
        if cls._contem(texto, "informática", "informatica", "computador", "notebook", "pc"):
            return "informatica"
        if cls._contem(texto, "game", "gamer", "console", "playstation", "xbox"):
            return "games"
        if cls._contem(texto, "celular", "smartphone", "iphone"):
            return "smartphones"
        if cls._contem(texto, "mercado", "supermercado"):
            return "mercado"
        if cls._contem(texto, "moda", "roupa", "calçado", "calcado"):
            return "moda"
        if cls._contem(texto, "beleza", "perfume", "cosmético", "cosmetico"):
            return "beleza"
        return None

    @staticmethod
    def _sem_acentos(texto: str) -> str:
        return (
            texto.replace("á", "a")
            .replace("à", "a")
            .replace("ã", "a")
            .replace("â", "a")
            .replace("é", "e")
            .replace("ê", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ô", "o")
            .replace("õ", "o")
            .replace("ú", "u")
            .replace("ç", "c")
        )
