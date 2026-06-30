from dataclasses import dataclass
from datetime import datetime, time, timedelta


@dataclass(frozen=True)
class DecisaoRepostProduto:
    pode_postar: bool
    motivo: str


class PoliticaRepostProdutoService:
    INTERVALO_MINIMO_REPOST = timedelta(hours=6)
    HORA_LIMITE_REPOST = time(hour=18)

    def avaliar(
        self,
        postagens_anteriores: list[datetime],
        agora: datetime,
    ) -> DecisaoRepostProduto:
        postagens_hoje = [
            posted_at for posted_at in postagens_anteriores if posted_at.date() == agora.date()
        ]

        if not postagens_hoje:
            return DecisaoRepostProduto(
                pode_postar=True,
                motivo="produto ainda nao foi postado hoje",
            )

        ultima_postagem = max(postagens_hoje)
        if agora.time() >= self.HORA_LIMITE_REPOST:
            return DecisaoRepostProduto(
                pode_postar=False,
                motivo="produto ja foi postado hoje e repost apos 18h nao e permitido",
            )

        tempo_desde_ultima = agora - ultima_postagem
        if tempo_desde_ultima >= self.INTERVALO_MINIMO_REPOST:
            return DecisaoRepostProduto(
                pode_postar=True,
                motivo="produto ja respeitou intervalo minimo de 6h para repost",
            )

        return DecisaoRepostProduto(
            pode_postar=False,
            motivo="produto ainda nao respeitou intervalo minimo de 6h para repost",
        )

    def pode_postar(self, postagens_anteriores: list[datetime], agora: datetime) -> bool:
        return self.avaliar(postagens_anteriores, agora).pode_postar
