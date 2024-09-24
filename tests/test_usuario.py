import pytest

from src.dominio.usuario.entidade import Usuario


def test_criacao_modelo_usuario():
    usuario = Usuario(
        id=1,
        nome="Joao",
        sobrenome="Silva",
        telefone="11992720099",
        email="joao@teste.com",
        senha="senha123",
    )
    assert usuario.id == 1
    assert usuario.nome == "Joao"
    assert usuario.sobrenome == "Silva"
    assert usuario.telefone == "11992720099"
    assert usuario.email == "joao@teste.com"
    assert usuario.senha == "senha123"


def test_usuario_email_format():
    with pytest.raises(ValueError):
        Usuario(
            id=1,
            nome="Joao",
            sobrenome="Silva",
            telefone="11000042526",
            email="email_invalido",
            senha="senha123",
        )


def test_usuario_telefone_format():
    with pytest.raises(ValueError) as excinfo:
        Usuario(
            id=1,
            nome="Joao",
            sobrenome="Silva",
            telefone="telefone_invalido",
            email="joao@teste.com",
            senha="senha123",
        )

    assert (
        str(excinfo.value)
        == "Formato de telefone celular inválido. Use apenas números: 2 ou 3 dígitos de DDD + 9 dígitos do número."
    )
