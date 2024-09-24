from sqlalchemy import Table, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import registry
from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.tipos import TipoTransacaoORM
from src.dominio.usuario.entidade import Usuario
from src.infra.database.connection import metadata

mapper = registry()

usuarios = Table(
    "usuarios",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("nome", String),
    Column("sobrenome", String),
    Column("telefone", String),
    Column("email", String),
    Column("senha", String),
)

transacoes = Table(
    "transacoes",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("usuario_id", Integer, ForeignKey("usuarios.id")),
    Column("valor", Float),
    Column("destino", String),
    Column("tipo", TipoTransacaoORM),
    Column("descricao", String),
    Column("caixa", DateTime),
)


def iniciar_mapeamento_orm():
    mapper.map_imperatively(Usuario, usuarios)
    mapper.map_imperatively(Transacao, transacoes)
