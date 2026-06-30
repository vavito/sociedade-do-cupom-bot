from src.dto.cupom_dto import CupomDTO, LojaCupom

LOJAS_SUPORTADAS_INICIAIS = {LojaCupom.AMAZON, LojaCupom.MERCADO_LIVRE}

PALAVRAS_TECH_CUPOM = {
    "amd",
    "amazon",
    "aircooler",
    "computador",
    "console",
    "controle",
    "cpu",
    "fan",
    "filtro de linha",
    "fone",
    "game",
    "gamer",
    "headset",
    "informatica",
    "informática",
    "iphone",
    "mercado livre",
    "monitor",
    "mouse",
    "mousepad",
    "notebook",
    "nvme",
    "pc",
    "placa",
    "placa mae",
    "placa mãe",
    "placa de video",
    "placa de vídeo",
    "power bank",
    "processador",
    "qcy",
    "refrigeracao",
    "refrigeração",
    "ssd",
    "suporte articulado",
    "teclado",
    "watercooler",
}

PALAVRAS_CUPOM_BLOQUEADAS = {
    "beleza",
    "calçado",
    "calcado",
    "cosmetico",
    "cosmético",
    "farmacia",
    "farmácia",
    "moda",
    "pet",
    "roupa",
    "tenis",
    "tênis",
}

CATEGORIAS_GENERICAS_ACEITAS = {None, "informatica", "games", "smartphones", "mercado"}


class CupomFilterService:
    def cupom_elegivel(self, cupom: CupomDTO) -> bool:
        if cupom.loja not in LOJAS_SUPORTADAS_INICIAIS:
            return False

        texto = f"{cupom.titulo} {cupom.descricao or ''}".casefold()
        if any(palavra in texto for palavra in PALAVRAS_CUPOM_BLOQUEADAS):
            return False

        if cupom.categoria_hint not in CATEGORIAS_GENERICAS_ACEITAS:
            return False

        return cupom.categoria_hint is None or any(
            palavra in texto for palavra in PALAVRAS_TECH_CUPOM
        )

    def filtrar(self, cupons: list[CupomDTO]) -> list[CupomDTO]:
        return [cupom for cupom in cupons if self.cupom_elegivel(cupom)]
