import pytest

from src.service.nicho_produto_service import NichoProduto, NichoProdutoService


@pytest.mark.parametrize(
    ("titulo", "nicho"),
    [
        ("Mouse gamer Logitech G203", NichoProduto.MOUSE_MOUSEPAD),
        ("Mousepad grande speed", NichoProduto.MOUSE_MOUSEPAD),
        ("Processador AMD Ryzen 7 5700", NichoProduto.PROCESSADOR),
        ("Teclado mecanico RGB switch brown", NichoProduto.TECLADO),
        ("Watercooler 240mm para processador", NichoProduto.REFRIGERACAO),
        ("Kit fans ARGB 120mm", NichoProduto.REFRIGERACAO),
        ("Placa de video RTX 4060", NichoProduto.PLACA_VIDEO),
        ("Placa mae Asus TUF Gaming B550M-Plus", NichoProduto.PLACA_MAE),
        ("Notebook Lenovo Ryzen 5", NichoProduto.NOTEBOOK),
        ("Monitor gamer 27 polegadas", NichoProduto.MONITOR),
        ("Fone QCY T13 bluetooth", NichoProduto.HEADSET_FONE),
        ("Headset gamer HyperX Cloud", NichoProduto.HEADSET_FONE),
        ("Gabinete gamer aquario", NichoProduto.GABINETE),
        ("SSD NVMe Kingston 1TB", NichoProduto.ARMAZENAMENTO),
        ("Controle sem fio para PC", NichoProduto.ACESSORIO),
        ("Filtro de linha 5 tomadas", NichoProduto.ACESSORIO),
        ("Power bank 20000mah", NichoProduto.ACESSORIO),
        ("Suporte articulado para monitor", NichoProduto.ACESSORIO),
    ],
)
def test_classifica_nichos_focados(titulo: str, nicho: NichoProduto) -> None:
    assert NichoProdutoService().classificar(titulo) == nicho.value


def test_nao_classifica_produto_fora_do_nicho() -> None:
    assert NichoProdutoService().classificar("Camiseta algodao masculina") is None
