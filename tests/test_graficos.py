from datetime import datetime
from random import choice, randint

import pytest

from src.dominio.graficos.services import (
    criar_grafico_fluxo_de_caixa,
    criar_grafico_receitas,
)
from src.dominio.transacao.tipos import TipoTransacao

@pytest.mark.skip
def test_grafico_fluxo_de_caixa(mock_usuario, transacao_gen):
    usuario = mock_usuario
    transacoes = []
    for i in range(150):
        transacoes.append(
            transacao_gen(
                usuario=usuario,
                valor=randint(150, 37400),
                destino=choice(
                    [
                        "Loja A",
                        "Loja B",
                        "Loja C",
                        "Vendedor",
                        "Fornecedor",
                        "Salário",
                        "Calça Jeans",
                    ]
                ),
                tipo=choice(["debito", "credito"]),
                caixa=datetime(
                    2024,
                    choice([j for j in range(1, 13)]),
                    choice([j for j in range(1, 28)]),
                ),
            )
        )

    grafico = criar_grafico_fluxo_de_caixa(transacoes)
    grafico["figura"].show()

@pytest.mark.skip
def test_grafico_receitas(mock_usuario, transacao_gen):
    usuario = mock_usuario
    transacoes = []
    for i in range(150):
        transacoes.append(
            transacao_gen(
                usuario=usuario,
                valor=randint(500, 1500),
                destino=choice(
                    [
                        "Loja A",
                        "Loja B",
                        "Loja C",
                        "Vendedor",
                        "Fornecedor",
                        "Salário",
                        "Calça Jeans",
                    ]
                ),
                tipo=choice([TipoTransacao.CREDITO, TipoTransacao.DEBITO]),
                caixa=datetime(
                    2024,
                    choice([j for j in range(1, 13)]),
                    choice([j for j in range(1, 28)]),
                ),
            )
        )

    grafico = criar_grafico_receitas(transacoes)
    grafico["figura"].show()
    grafico["figura"].write_image("/tmp/teste.png")
