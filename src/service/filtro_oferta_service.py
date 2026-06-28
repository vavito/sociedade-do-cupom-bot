from src.dto.oferta_dto import OfertaDTO

PALAVRAS_TECNOLOGIA = {
    "ssd",
    "nvme",
    "m.2",
    "ram",
    "memoria",
    "memória",
    "processador",
    "cpu",
    "placa-mae",
    "placa mãe",
    "motherboard",
    "gpu",
    "placa de video",
    "placa de vídeo",
    "fonte",
    "gabinete",
    "cooler",
    "teclado",
    "keyboard",
    "mouse",
    "headset",
    "monitor",
    "pc gamer",
}

PALAVRAS_BLOQUEADAS = {
    "roupa",
    "sapato",
    "bolsa",
    "brinquedo",
    "pet",
    "cozinha",
    "jardim",
    "celular",
    "capa",
    "pelicula",
    "película",
    "automotivo",
    "arduino",
    "raspberry",
    "oled",
    "painel led",
}


class FiltroOfertaService:
    def oferta_elegivel(self, oferta: OfertaDTO) -> bool:
        texto = f"{oferta.produto.titulo} {oferta.produto.categoria or ''}".casefold()
        if any(palavra in texto for palavra in PALAVRAS_BLOQUEADAS):
            return False
        return any(palavra in texto for palavra in PALAVRAS_TECNOLOGIA)

    def filtrar(self, ofertas: list[OfertaDTO]) -> list[OfertaDTO]:
        return [oferta for oferta in ofertas if self.oferta_elegivel(oferta)]
