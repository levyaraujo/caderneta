from sqlalchemy import (
    Table,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import registry, relationship
from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.tipos import TipoTransacaoORM
from src.dominio.usuario.entidade import Usuario
from src.infra.database.connection import metadata

mapper = registry(metadata=metadata)

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
    Column("competencia", DateTime),
    Column("apagado", Boolean, default=False),
)


def iniciar_mapeamento_orm():
    if not mapper.mappers:
        mapper.map_imperatively(
            Usuario,
            usuarios,
            properties={
                "transacoes": relationship(Transacao, back_populates="usuario")
            },
        )
        mapper.map_imperatively(
            Transacao,
            transacoes,
            properties={
                "usuario": relationship(Usuario, back_populates="transacoes"),
                "usuario_id": transacoes.c.usuario_id,
            },
        )
