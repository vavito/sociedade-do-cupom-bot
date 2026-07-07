from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.cupom_postagem_historico_service import CupomPostagemHistoricoService
from src.service.cupom_postagem_service import CupomPostagemResultado, CupomPostagemService
from src.service.cupom_preview_runner_service import (
    CupomPreviewRunnerResultado,
    CupomPreviewRunnerService,
)
from src.service.produto_candidato_update_service import (
    ProdutoCandidatoUpdateResultado,
    ProdutoCandidatoUpdateService,
)


@dataclass(frozen=True)
class CupomRotinaDiariaResultado:
    produtos: ProdutoCandidatoUpdateResultado
    previews: CupomPreviewRunnerResultado
    postagens: list[CupomPostagemResultado]


class CupomRotinaDiariaService:
    def __init__(
        self,
        produto_update_service: ProdutoCandidatoUpdateService,
        preview_runner: CupomPreviewRunnerService,
        historico_service: CupomPostagemHistoricoService | None = None,
        postagem_service: CupomPostagemService | None = None,
    ) -> None:
        self.produto_update_service = produto_update_service
        self.preview_runner = preview_runner
        self.historico_service = historico_service or CupomPostagemHistoricoService()
        self.postagem_service = postagem_service

    async def executar(
        self,
        caminho_fontes: str | Path,
        caminho_produtos: str | Path,
        caminho_historico: str | Path,
        data_referencia: date | None = None,
        limite_por_fonte: int = 5,
        limite_posts: int = 3,
        manter_existentes: bool = False,
        salvar_produtos: bool = True,
        confirmar_envio: bool = False,
        filtrar_cupons: bool = True,
        fontes: list[FonteProdutoDTO] | None = None,
        agora: datetime | None = None,
    ) -> CupomRotinaDiariaResultado:
        momento = agora or datetime.now()
        if fontes is None:
            produtos_resultado = await self.produto_update_service.atualizar(
                caminho_fontes=caminho_fontes,
                caminho_saida=caminho_produtos,
                data_referencia=data_referencia,
                limite_por_fonte=limite_por_fonte,
                manter_existentes=manter_existentes,
                salvar=salvar_produtos,
            )
        else:
            produtos_resultado = await self.produto_update_service.atualizar_por_fontes(
                fontes=fontes,
                caminho_saida=caminho_produtos,
                data_referencia=data_referencia,
                limite_por_fonte=limite_por_fonte,
                manter_existentes=manter_existentes,
                salvar=salvar_produtos,
            )

        postagens_por_produto = self.historico_service.carregar_de_arquivo(caminho_historico)
        previews_resultado = await self.preview_runner.gerar_previews(
            caminho_produtos=caminho_produtos,
            data_referencia=data_referencia,
            postagens_por_produto=postagens_por_produto,
            agora=momento,
            limite=limite_posts,
            filtrar_cupons=filtrar_cupons,
        )

        if not confirmar_envio or not previews_resultado.previews:
            return CupomRotinaDiariaResultado(
                produtos=produtos_resultado,
                previews=previews_resultado,
                postagens=[],
            )

        if self.postagem_service is None:
            raise RuntimeError("Postagem service precisa estar configurado para confirmar envio.")

        resultados = []
        historico_atualizado = postagens_por_produto
        for match, mensagem in previews_resultado.previews:
            resultado_postagem = await self.postagem_service.publicar(mensagem)
            resultados.append(resultado_postagem)
            historico_atualizado = self.historico_service.registrar_postagem(
                historico_atualizado,
                self._chave_produto(match.produto),
                momento,
            )
            self.historico_service.salvar_em_arquivo(caminho_historico, historico_atualizado)

        return CupomRotinaDiariaResultado(
            produtos=produtos_resultado,
            previews=previews_resultado,
            postagens=resultados,
        )

    @staticmethod
    def _chave_produto(produto: ProdutoCandidatoDTO) -> str:
        return f"{produto.loja}:{produto.external_id}"
