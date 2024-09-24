from datetime import datetime
from random import randint

import pytest

from src.dominio.transacao.entidade import Transacao
from src.dominio.usuario.entidade import Usuario


@pytest.fixture
def usuario():
    return Usuario(
        id=randint(1, 10000),
        nome="Joao",
        sobrenome="Silva",
        telefone="94981362600",
        email="joao@teste.com",
        senha="senha123"
    )

@pytest.fixture(scope="function")
def transacao_gen():

    def make_mock(usuario, valor, destino, tipo, caixa=datetime(2024, 10, 22)):
        return Transacao(
            id=randint(1, 1000),
            usuario=usuario,
            valor=valor,
            destino=destino,
            tipo=tipo,
            descricao="asodihasjklfnasfr",
            caixa=caixa
        )

    return make_mock