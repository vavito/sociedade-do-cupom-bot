from enum import StrEnum


class NichoProduto(StrEnum):
    MOUSE_MOUSEPAD = "mouse_mousepad"
    PROCESSADOR = "processador"
    TECLADO = "teclado"
    REFRIGERACAO = "refrigeracao"
    PLACA_VIDEO = "placa_video"
    PLACA_MAE = "placa_mae"
    NOTEBOOK = "notebook"
    MONITOR = "monitor"
    HEADSET_FONE = "headset_fone"
    GABINETE = "gabinete"
    ARMAZENAMENTO = "armazenamento"
    ACESSORIO = "acessorio"


TERMOS_NICHO_PRODUTO = {
    NichoProduto.MOUSE_MOUSEPAD: {
        "mouse",
        "mousepad",
        "deskpad",
    },
    NichoProduto.PROCESSADOR: {
        "processador",
        "cpu",
        "ryzen",
        "intel core",
        "core i3",
        "core i5",
        "core i7",
        "core i9",
    },
    NichoProduto.TECLADO: {
        "teclado",
        "keyboard",
        "switch",
        "keycap",
    },
    NichoProduto.REFRIGERACAO: {
        "air cooler",
        "aircooler",
        "cooler",
        "fan",
        "fans",
        "pasta termica",
        "water cooler",
        "watercooler",
    },
    NichoProduto.PLACA_VIDEO: {
        "gpu",
        "placa de video",
        "placa de vídeo",
        "radeon",
        "rtx",
        "rx 5",
        "rx 6",
        "rx 7",
        "gtx",
    },
    NichoProduto.PLACA_MAE: {
        "b450",
        "b550",
        "b650",
        "h610",
        "motherboard",
        "placa mae",
        "placa mãe",
        "x570",
        "x670",
        "z690",
        "z790",
    },
    NichoProduto.NOTEBOOK: {
        "laptop",
        "notebook",
    },
    NichoProduto.MONITOR: {
        "monitor",
    },
    NichoProduto.HEADSET_FONE: {
        "earbuds",
        "fone",
        "headphone",
        "headset",
        "qcy",
    },
    NichoProduto.GABINETE: {
        "case gamer",
        "gabinete",
    },
    NichoProduto.ARMAZENAMENTO: {
        "hd externo",
        "m.2",
        "nvme",
        "ssd",
    },
    NichoProduto.ACESSORIO: {
        "controle",
        "filtro de linha",
        "hub usb",
        "power bank",
        "suporte articulado",
        "suporte de monitor",
        "suporte para monitor",
    },
}

ORDEM_CLASSIFICACAO_NICHO = [
    NichoProduto.ACESSORIO,
    NichoProduto.REFRIGERACAO,
    NichoProduto.NOTEBOOK,
    NichoProduto.PLACA_VIDEO,
    NichoProduto.PLACA_MAE,
    NichoProduto.ARMAZENAMENTO,
    NichoProduto.MOUSE_MOUSEPAD,
    NichoProduto.TECLADO,
    NichoProduto.HEADSET_FONE,
    NichoProduto.GABINETE,
    NichoProduto.MONITOR,
    NichoProduto.PROCESSADOR,
]


class NichoProdutoService:
    def classificar(
        self, titulo: str, categoria: str | None = None, marca: str | None = None
    ) -> str | None:
        texto = f"{titulo} {categoria or ''} {marca or ''}".casefold()
        for nicho in ORDEM_CLASSIFICACAO_NICHO:
            termos = TERMOS_NICHO_PRODUTO[nicho]
            if any(termo in texto for termo in termos):
                return nicho.value
        return None

    def produto_elegivel(
        self,
        titulo: str,
        categoria: str | None = None,
        marca: str | None = None,
    ) -> bool:
        return self.classificar(titulo, categoria, marca) is not None
