from src.dto.oferta_dto import OfertaDTO


class ScoreOfertaService:
    def calcular(self, oferta: OfertaDTO) -> int:
        score = 0

        if oferta.desconto_percentual:
            score += min(oferta.desconto_percentual, 50)
        if oferta.volume_vendas:
            score += min(oferta.volume_vendas // 10, 25)
        if oferta.avaliacao_percentual and oferta.avaliacao_percentual >= 90:
            score += 15
        if oferta.cupom_codigo:
            score += 10
        if oferta.comissao_percentual:
            score += min(int(oferta.comissao_percentual), 10)

        return min(score, 100)

    def aplicar_score(self, ofertas: list[OfertaDTO]) -> list[OfertaDTO]:
        return [oferta.model_copy(update={"score": self.calcular(oferta)}) for oferta in ofertas]
