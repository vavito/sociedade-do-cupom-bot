from decimal import Decimal

from src.dto.oferta_dto import OfertaDTO
from src.dto.telegram_message_dto import TelegramMessageDTO


def mapear_oferta_para_telegram(oferta: OfertaDTO) -> TelegramMessageDTO:
    linhas = [
        f"🔥 {oferta.produto.titulo}",
        "",
        f"💵 {_formatar_preco(oferta.preco_atual, oferta.moeda)}",
    ]
    if oferta.cupom_codigo:
        linhas.append(f"🎟️ Cupom: {oferta.cupom_codigo}")
    linhas.extend(["", str(oferta.afiliado_url), "", "(Anuncio)"])
    return TelegramMessageDTO(image_url=oferta.produto.imagem_url, caption="\n".join(linhas))


def _formatar_preco(valor: Decimal, moeda: str) -> str:
    simbolo = "R$" if moeda.upper() == "BRL" else moeda.upper()
    texto = f"{valor:.0f}" if valor == valor.to_integral() else f"{valor:.2f}".replace(".", ",")
    return f"{simbolo} {texto}"
